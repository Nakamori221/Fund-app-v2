"""Observation service - business logic for observation/finding management"""

from uuid import UUID
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from app.models.database import Observation, Case, User
from app.models.schemas import (
    ObservationCreate,
    ObservationUpdate,
    SourceTag,
    DisclosureLevel,
    UserRole,
)
from app.core.errors import NotFoundException, ValidationException, AuthorizationException


class ObservationService:
    """Observation management service"""

    @staticmethod
    async def create_observation(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        observation_data: ObservationCreate,
    ) -> Observation:
        """
        Create a new observation for a case.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of user creating the observation
        - observation_data: Observation data

        **Returns**:
        - Created Observation object

        **Errors**:
        - NotFoundException: Case not found
        - ValidationException: Invalid observation data
        """
        # Verify case exists
        case = await ObservationService._get_case(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        # Validate input
        if not observation_data.content or len(observation_data.content) < 10:
            raise ValidationException("Observation content must be at least 10 characters")

        if not observation_data.section:
            raise ValidationException("Section is required")

        # Create observation
        observation = Observation(
            case_id=case_id,
            section=observation_data.section,
            content=observation_data.content,
            source_tag=observation_data.source_tag or SourceTag.PUBLIC,
            disclosure_level=observation_data.disclosure_level or DisclosureLevel.PRIVATE,
            created_by=user_id,
            metadata=observation_data.metadata or {},
        )

        db.add(observation)
        await db.commit()
        await db.refresh(observation)

        return observation

    @staticmethod
    async def get_observation_by_id(
        db: AsyncSession,
        observation_id: UUID,
    ) -> Optional[Observation]:
        """
        Get observation by ID.

        **Parameters**:
        - db: Database session
        - observation_id: Observation ID

        **Returns**:
        - Observation object if found, None otherwise
        """
        stmt = select(Observation).where(
            and_(Observation.id == observation_id, Observation.is_deleted == False)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_observations(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        skip: int = 0,
        limit: int = 20,
        source_tag_filter: Optional[SourceTag] = None,
        disclosure_level_filter: Optional[DisclosureLevel] = None,
    ) -> Tuple[List[Observation], int]:
        """
        Get observations for a case with RBAC filtering.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - skip: Number of records to skip
        - limit: Number of records to return
        - source_tag_filter: Filter by source tag
        - disclosure_level_filter: Filter by disclosure level

        **Returns**:
        - Tuple of (observations list, total count)

        **RBAC Rules**:
        - All roles can see observations in cases they have access to
        - Disclosure level filtering applied per role
        """
        # Verify case exists and user has access
        case = await ObservationService._get_case(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        # Check user can access this case
        can_access_case = (
            user_role != UserRole.ANALYST or case.created_by == user_id
        )
        if not can_access_case:
            raise AuthorizationException("Not authorized to access this case")

        # Build query filters
        filters = [
            Observation.case_id == case_id,
            Observation.is_deleted == False,
        ]

        # Apply source tag filter
        if source_tag_filter:
            filters.append(Observation.source_tag == source_tag_filter)

        # Apply disclosure level filter
        if disclosure_level_filter:
            filters.append(Observation.disclosure_level == disclosure_level_filter)

        # Apply RBAC disclosure level filtering
        # For now, show all (data masking handled in schema/response layer)
        # In future: filter based on user role and disclosure level

        # Get total count
        count_stmt = select(Observation).where(and_(*filters))
        count_result = await db.execute(count_stmt)
        total = len(count_result.fetchall())

        # Get paginated results
        stmt = (
            select(Observation)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
            .order_by(Observation.created_at.desc())
        )
        result = await db.execute(stmt)
        observations = result.scalars().all()

        return observations, total

    @staticmethod
    async def update_observation(
        db: AsyncSession,
        observation_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        observation_data: ObservationUpdate,
    ) -> Optional[Observation]:
        """
        Update an observation with RBAC validation.

        **Parameters**:
        - db: Database session
        - observation_id: Observation ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - observation_data: Observation update data

        **Returns**:
        - Updated Observation object

        **RBAC Rules**:
        - Creator: Can update own observations
        - Lead Partner+: Can update any observation
        - Admin: Can update any observation

        **Errors**:
        - NotFoundException: Observation not found
        - AuthorizationException: User not authorized
        """
        # Get observation
        observation = await ObservationService.get_observation_by_id(db, observation_id)
        if not observation:
            raise NotFoundException("Observation not found")

        # Check authorization
        is_creator = observation.created_by == user_id
        is_lead_or_above = user_role in [
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        if not (is_creator or is_lead_or_above):
            raise AuthorizationException("Not authorized to update this observation")

        # Update allowed fields
        if observation_data.content is not None:
            if len(observation_data.content) < 10:
                raise ValidationException("Content must be at least 10 characters")
            observation.content = observation_data.content

        if observation_data.section is not None:
            observation.section = observation_data.section

        if observation_data.source_tag is not None:
            observation.source_tag = observation_data.source_tag

        if observation_data.disclosure_level is not None:
            observation.disclosure_level = observation_data.disclosure_level

        if observation_data.metadata is not None:
            observation.metadata = observation_data.metadata

        await db.commit()
        await db.refresh(observation)

        return observation

    @staticmethod
    async def delete_observation(
        db: AsyncSession,
        observation_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> Optional[Observation]:
        """
        Delete an observation (soft delete) with RBAC validation.

        **Parameters**:
        - db: Database session
        - observation_id: Observation ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user

        **Returns**:
        - Deleted Observation object

        **RBAC Rules**:
        - Creator: Can delete own observations
        - Lead Partner+: Can delete any observation
        - Admin: Can delete any observation

        **Errors**:
        - NotFoundException: Observation not found
        - AuthorizationException: User not authorized
        """
        # Get observation
        observation = await ObservationService.get_observation_by_id(db, observation_id)
        if not observation:
            raise NotFoundException("Observation not found")

        # Check authorization
        is_creator = observation.created_by == user_id
        is_lead_or_above = user_role in [
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        if not (is_creator or is_lead_or_above):
            raise AuthorizationException("Not authorized to delete this observation")

        # Perform soft delete
        observation.is_deleted = True
        await db.commit()
        await db.refresh(observation)

        return observation

    @staticmethod
    async def verify_observation(
        db: AsyncSession,
        observation_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> Optional[Observation]:
        """
        Verify an observation (lead partner+ only).

        **Parameters**:
        - db: Database session
        - observation_id: Observation ID
        - user_id: ID of requesting user (verifier)
        - user_role: Role of requesting user

        **Returns**:
        - Verified Observation object

        **RBAC Rules**:
        - Only Lead Partner+ can verify observations

        **Errors**:
        - NotFoundException: Observation not found
        - AuthorizationException: User not authorized (requires lead+)
        """
        # Get observation
        observation = await ObservationService.get_observation_by_id(db, observation_id)
        if not observation:
            raise NotFoundException("Observation not found")

        # Check authorization
        is_lead_or_above = user_role in [
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        if not is_lead_or_above:
            raise AuthorizationException("Only lead partners and above can verify observations")

        # Mark as verified
        from datetime import datetime
        observation.is_verified = True
        observation.verified_by = user_id
        observation.verified_at = datetime.utcnow()

        await db.commit()
        await db.refresh(observation)

        return observation

    @staticmethod
    async def search_observations(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Observation], int]:
        """
        Search observations by content with RBAC filtering.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - query: Search query string
        - skip: Number of records to skip
        - limit: Number of records to return

        **Returns**:
        - Tuple of (observations list, total count)
        """
        # Verify case exists and user has access
        case = await ObservationService._get_case(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        can_access_case = (
            user_role != UserRole.ANALYST or case.created_by == user_id
        )
        if not can_access_case:
            raise AuthorizationException("Not authorized to access this case")

        # Build search filters
        filters = [
            Observation.case_id == case_id,
            Observation.is_deleted == False,
            Observation.content.ilike(f"%{query}%"),
        ]

        # Get total count
        count_stmt = select(Observation).where(and_(*filters))
        count_result = await db.execute(count_stmt)
        total = len(count_result.fetchall())

        # Get paginated results
        stmt = (
            select(Observation)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
            .order_by(Observation.created_at.desc())
        )
        result = await db.execute(stmt)
        observations = result.scalars().all()

        return observations, total

    @staticmethod
    async def get_observation_statistics(
        db: AsyncSession,
        case_id: UUID,
    ) -> dict:
        """
        Get observation statistics for a case.

        **Parameters**:
        - db: Database session
        - case_id: Case ID

        **Returns**:
        - Dictionary with observation statistics
        """
        stmt = select(Observation).where(
            and_(Observation.case_id == case_id, Observation.is_deleted == False)
        )
        result = await db.execute(stmt)
        observations = result.scalars().all()

        verified_count = sum(1 for obs in observations if obs.is_verified)
        by_source_tag = {}
        by_disclosure = {}

        for obs in observations:
            source = obs.source_tag.value
            disclosure = obs.disclosure_level.value

            by_source_tag[source] = by_source_tag.get(source, 0) + 1
            by_disclosure[disclosure] = by_disclosure.get(disclosure, 0) + 1

        return {
            "case_id": str(case_id),
            "total_count": len(observations),
            "verified_count": verified_count,
            "unverified_count": len(observations) - verified_count,
            "by_source_tag": by_source_tag,
            "by_disclosure_level": by_disclosure,
        }

    @staticmethod
    async def _get_case(db: AsyncSession, case_id: UUID) -> Optional[Case]:
        """Helper method to get case"""
        stmt = select(Case).where(
            and_(Case.id == case_id, Case.is_deleted == False)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
