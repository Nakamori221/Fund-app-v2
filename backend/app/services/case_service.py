"""Case service - business logic for case management"""

from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from app.models.database import Case, User
from app.models.schemas import CaseCreate, CaseUpdate, CaseStatus, UserRole
from app.core.errors import NotFoundException, ValidationException, AuthorizationException


class CaseService:
    """Case management service"""

    @staticmethod
    async def create_case(
        db: AsyncSession,
        user_id: UUID,
        case_data: CaseCreate,
    ) -> Case:
        """
        Create a new case.

        **Parameters**:
        - db: Database session
        - user_id: ID of user creating the case
        - case_data: Case creation data

        **Returns**:
        - Created Case object

        **Errors**:
        - ValidationException: Invalid case data
        """
        # Validate input
        if not case_data.title or len(case_data.title) < 5:
            raise ValidationException("Case title must be at least 5 characters")

        if not case_data.company_name:
            raise ValidationException("Company name is required")

        # Create case
        case = Case(
            title=case_data.title,
            description=case_data.description,
            company_name=case_data.company_name,
            sector=case_data.sector,
            status=case_data.status or CaseStatus.DRAFT,
            created_by=user_id,
            metadata=case_data.metadata or {},
        )

        db.add(case)
        await db.commit()
        await db.refresh(case)

        return case

    @staticmethod
    async def get_case_by_id(
        db: AsyncSession,
        case_id: UUID,
    ) -> Optional[Case]:
        """
        Get case by ID.

        **Parameters**:
        - db: Database session
        - case_id: Case ID

        **Returns**:
        - Case object if found, None otherwise
        """
        stmt = select(Case).where(
            and_(Case.id == case_id, Case.is_deleted == False)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_cases(
        db: AsyncSession,
        user_id: UUID,
        user_role: UserRole,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[CaseStatus] = None,
    ) -> tuple[List[Case], int]:
        """
        Get cases with RBAC filtering.

        **Parameters**:
        - db: Database session
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - skip: Number of records to skip
        - limit: Number of records to return
        - status_filter: Filter by case status

        **Returns**:
        - Tuple of (cases list, total count)

        **RBAC Rules**:
        - analyst: Can only see own cases
        - lead_partner+: Can see all cases
        - admin: Can see all cases
        """
        # Build base query
        filters = [Case.is_deleted == False]

        # Apply status filter if provided
        if status_filter:
            filters.append(Case.status == status_filter)

        # Apply RBAC
        if user_role == UserRole.ANALYST:
            # Analysts can only see their own cases
            filters.append(Case.created_by == user_id)
        # lead_partner, ic_member, admin can see all cases (no additional filter)

        # Get total count
        count_stmt = select(Case).where(and_(*filters))
        count_result = await db.execute(count_stmt)
        total = len(count_result.fetchall())

        # Get paginated results
        stmt = (
            select(Case)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
            .order_by(Case.created_at.desc())
        )
        result = await db.execute(stmt)
        cases = result.scalars().all()

        return cases, total

    @staticmethod
    async def update_case(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        case_data: CaseUpdate,
    ) -> Optional[Case]:
        """
        Update a case with RBAC validation.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - case_data: Case update data

        **Returns**:
        - Updated Case object

        **RBAC Rules**:
        - Creator (analyst): Can update own draft cases
        - lead_partner+: Can change case status
        - admin: Can update any case

        **Errors**:
        - NotFoundException: Case not found
        - AuthorizationException: User not authorized to update case
        """
        # Get case
        case = await CaseService.get_case_by_id(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        # Check authorization
        is_creator = case.created_by == user_id
        is_admin = user_role == UserRole.ADMIN
        is_lead_or_above = user_role in [UserRole.LEAD_PARTNER, UserRole.IC_MEMBER, UserRole.ADMIN]

        if not (is_creator or is_lead_or_above or is_admin):
            raise AuthorizationException("Not authorized to update this case")

        # Creator can only update draft cases
        if is_creator and not is_lead_or_above:
            if case.status != CaseStatus.DRAFT:
                raise AuthorizationException("Can only update draft cases")

        # Update allowed fields
        if case_data.title is not None:
            case.title = case_data.title

        if case_data.description is not None:
            case.description = case_data.description

        if case_data.status is not None:
            # Only leads and admins can change status
            if not is_lead_or_above:
                raise AuthorizationException("Not authorized to change case status")
            case.status = case_data.status

        if case_data.metadata is not None:
            case.metadata = case_data.metadata

        await db.commit()
        await db.refresh(case)

        return case

    @staticmethod
    async def delete_case(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> Optional[Case]:
        """
        Delete a case (soft delete) with RBAC validation.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user

        **Returns**:
        - Deleted Case object

        **RBAC Rules**:
        - Creator (analyst): Can delete own draft cases
        - admin: Can delete any case

        **Errors**:
        - NotFoundException: Case not found
        - AuthorizationException: User not authorized to delete case
        """
        # Get case
        case = await CaseService.get_case_by_id(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        # Check authorization
        is_creator = case.created_by == user_id
        is_admin = user_role == UserRole.ADMIN

        if not (is_creator or is_admin):
            raise AuthorizationException("Not authorized to delete this case")

        # Creators can only delete draft cases
        if is_creator and not is_admin:
            if case.status != CaseStatus.DRAFT:
                raise AuthorizationException("Can only delete draft cases")

        # Perform soft delete
        case.is_deleted = True
        await db.commit()
        await db.refresh(case)

        return case

    @staticmethod
    async def search_cases(
        db: AsyncSession,
        user_id: UUID,
        user_role: UserRole,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Case], int]:
        """
        Search cases by title or company name with RBAC filtering.

        **Parameters**:
        - db: Database session
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - query: Search query string
        - skip: Number of records to skip
        - limit: Number of records to return

        **Returns**:
        - Tuple of (cases list, total count)
        """
        filters = [Case.is_deleted == False]

        # Apply search filters
        search_filter = or_(
            Case.title.ilike(f"%{query}%"),
            Case.company_name.ilike(f"%{query}%"),
        )
        filters.append(search_filter)

        # Apply RBAC
        if user_role == UserRole.ANALYST:
            filters.append(Case.created_by == user_id)

        # Get total count
        count_stmt = select(Case).where(and_(*filters))
        count_result = await db.execute(count_stmt)
        total = len(count_result.fetchall())

        # Get paginated results
        stmt = (
            select(Case)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
            .order_by(Case.created_at.desc())
        )
        result = await db.execute(stmt)
        cases = result.scalars().all()

        return cases, total

    @staticmethod
    async def get_case_statistics(
        db: AsyncSession,
        case_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get case statistics (observation count, conflict count, etc.).

        **Parameters**:
        - db: Database session
        - case_id: Case ID

        **Returns**:
        - Dictionary with case statistics
        """
        case = await CaseService.get_case_by_id(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        return {
            "case_id": str(case_id),
            "observation_count": len(case.observations),
            "conflict_count": len(case.conflicts),
            "report_count": len(case.reports),
            "status": case.status.value,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
        }
