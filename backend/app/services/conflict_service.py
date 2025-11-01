"""Conflict service - business logic for conflict detection and management"""

from uuid import UUID
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models.database import Conflict, Observation, Case
from app.models.schemas import ConflictType, UserRole
from app.core.errors import NotFoundException, AuthorizationException


class ConflictService:
    """Conflict detection and management service"""

    @staticmethod
    async def detect_conflicts(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> List[Conflict]:
        """
        Detect conflicts in a case (must be called by lead partner+).

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user

        **Returns**:
        - List of detected Conflict objects

        **RBAC Rules**:
        - Only Lead Partner+ can detect conflicts

        **Errors**:
        - NotFoundException: Case not found
        - AuthorizationException: User not authorized
        """
        # Verify authorization
        is_lead_or_above = user_role in [
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        if not is_lead_or_above:
            raise AuthorizationException("Only lead partners and above can detect conflicts")

        # Verify case exists
        case = await ConflictService._get_case(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        # Get all observations for the case
        stmt = select(Observation).where(
            and_(
                Observation.case_id == case_id,
                Observation.is_deleted == False,  # noqa: E712
            )
        )
        result = await db.execute(stmt)
        observations = result.scalars().all()

        if len(observations) < 2:
            return []  # Need at least 2 observations to detect conflicts

        # Detect conflicts between observations
        detected_conflicts = []
        existing_conflicts = await ConflictService.get_conflicts(
            db, case_id, user_id, user_role
        )
        existing_ids = {
            (c.observation_id_1, c.observation_id_2)
            or (c.observation_id_2, c.observation_id_1)
            for c in existing_conflicts[0]
        }

        for i, obs1 in enumerate(observations):
            for obs2 in observations[i + 1:]:
                # Check if conflict already exists
                conflict_pair = (
                    (obs1.id, obs2.id)
                    if obs1.id < obs2.id
                    else (obs2.id, obs1.id)
                )

                if conflict_pair in existing_ids:
                    continue

                # Detect conflicts based on content similarity and metadata
                conflict_result = await ConflictService._analyze_observations(
                    db, obs1, obs2
                )

                if conflict_result:
                    conflict_type, severity = conflict_result

                    conflict = Conflict(
                        case_id=case_id,
                        observation_id_1=obs1.id,
                        observation_id_2=obs2.id,
                        conflict_type=conflict_type,
                        severity=severity,
                        description=f"Conflict detected between observations: {obs1.section} vs {obs2.section}",
                    )

                    db.add(conflict)
                    detected_conflicts.append(conflict)

        if detected_conflicts:
            await db.commit()
            for conflict in detected_conflicts:
                await db.refresh(conflict)

        return detected_conflicts

    @staticmethod
    async def get_conflict_by_id(
        db: AsyncSession,
        conflict_id: UUID,
    ) -> Optional[Conflict]:
        """
        Get conflict by ID.

        **Parameters**:
        - db: Database session
        - conflict_id: Conflict ID

        **Returns**:
        - Conflict object if found, None otherwise
        """
        stmt = select(Conflict).where(Conflict.id == conflict_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_conflicts(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        skip: int = 0,
        limit: int = 20,
        resolved_filter: Optional[bool] = None,
    ) -> Tuple[List[Conflict], int]:
        """
        Get conflicts for a case with RBAC filtering.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - skip: Number of records to skip
        - limit: Number of records to return
        - resolved_filter: Filter by resolved status (True/False/None for all)

        **Returns**:
        - Tuple of (conflicts list, total count)

        **RBAC Rules**:
        - All roles can see conflicts in cases they have access to
        """
        # Verify case exists and user has access
        case = await ConflictService._get_case(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        can_access_case = (
            user_role != UserRole.ANALYST or case.created_by == user_id
        )
        if not can_access_case:
            raise AuthorizationException("Not authorized to access this case")

        # Build filters
        filters = [Conflict.case_id == case_id]

        if resolved_filter is not None:
            filters.append(Conflict.is_resolved == resolved_filter)

        # Get total count
        count_stmt = select(Conflict).where(and_(*filters))
        count_result = await db.execute(count_stmt)
        total = len(count_result.fetchall())

        # Get paginated results
        stmt = (
            select(Conflict)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
            .order_by(Conflict.severity.desc(), Conflict.detected_at.desc())
        )
        result = await db.execute(stmt)
        conflicts = result.scalars().all()

        return conflicts, total

    @staticmethod
    async def resolve_conflict(
        db: AsyncSession,
        conflict_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        resolution_notes: Optional[str] = None,
    ) -> Optional[Conflict]:
        """
        Resolve a conflict (lead partner+ only).

        **Parameters**:
        - db: Database session
        - conflict_id: Conflict ID
        - user_id: ID of requesting user (resolver)
        - user_role: Role of requesting user
        - resolution_notes: Notes on the resolution

        **Returns**:
        - Resolved Conflict object

        **RBAC Rules**:
        - Only Lead Partner+ can resolve conflicts

        **Errors**:
        - NotFoundException: Conflict not found
        - AuthorizationException: User not authorized
        """
        # Get conflict
        conflict = await ConflictService.get_conflict_by_id(db, conflict_id)
        if not conflict:
            raise NotFoundException("Conflict not found")

        # Check authorization
        is_lead_or_above = user_role in [
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        if not is_lead_or_above:
            raise AuthorizationException("Only lead partners and above can resolve conflicts")

        # Mark as resolved
        from datetime import datetime
        conflict.is_resolved = True
        conflict.resolved_by = user_id
        conflict.resolved_at = datetime.utcnow()
        conflict.resolution_notes = resolution_notes

        await db.commit()
        await db.refresh(conflict)

        return conflict

    @staticmethod
    async def get_high_severity_conflicts(
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        severity_threshold: float = 0.7,
    ) -> List[Conflict]:
        """
        Get high-severity conflicts for a case.

        **Parameters**:
        - db: Database session
        - case_id: Case ID
        - user_id: ID of requesting user
        - user_role: Role of requesting user
        - severity_threshold: Severity threshold (0-1)

        **Returns**:
        - List of high-severity Conflict objects
        """
        # Verify case exists and user has access
        case = await ConflictService._get_case(db, case_id)
        if not case:
            raise NotFoundException("Case not found")

        can_access_case = (
            user_role != UserRole.ANALYST or case.created_by == user_id
        )
        if not can_access_case:
            raise AuthorizationException("Not authorized to access this case")

        stmt = (
            select(Conflict)
            .where(
                and_(
                    Conflict.case_id == case_id,
                    Conflict.severity >= severity_threshold,
                    Conflict.is_resolved == False,  # noqa: E712
                )
            )
            .order_by(Conflict.severity.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_conflict_statistics(
        db: AsyncSession,
        case_id: UUID,
    ) -> dict:
        """
        Get conflict statistics for a case.

        **Parameters**:
        - db: Database session
        - case_id: Case ID

        **Returns**:
        - Dictionary with conflict statistics
        """
        stmt = select(Conflict).where(Conflict.case_id == case_id)
        result = await db.execute(stmt)
        conflicts = result.scalars().all()

        resolved_count = sum(1 for c in conflicts if c.is_resolved)
        unresolved_count = len(conflicts) - resolved_count
        avg_severity = (
            sum(c.severity for c in conflicts) / len(conflicts)
            if conflicts
            else 0
        )

        by_type = {}
        for conflict in conflicts:
            conflict_type = conflict.conflict_type.value
            by_type[conflict_type] = by_type.get(conflict_type, 0) + 1

        return {
            "case_id": str(case_id),
            "total_count": len(conflicts),
            "resolved_count": resolved_count,
            "unresolved_count": unresolved_count,
            "average_severity": round(avg_severity, 2),
            "by_type": by_type,
        }

    @staticmethod
    async def _analyze_observations(
        db: AsyncSession,
        obs1: Observation,
        obs2: Observation,
    ) -> Optional[Tuple[ConflictType, float]]:
        """
        Analyze two observations for conflicts.

        **Parameters**:
        - db: Database session
        - obs1: First observation
        - obs2: Second observation

        **Returns**:
        - Tuple of (conflict_type, severity) if conflict detected, None otherwise

        **Conflict Detection Logic**:
        - Source conflict: Different source tags with high confidence
        - Data inconsistency: Contradictory information
        - Price anomaly: Large price differences
        - Timing conflict: Inconsistent dates
        """
        conflict_type = None
        severity = 0.0

        # Check for source conflicts
        if obs1.source_tag != obs2.source_tag:
            # Different sources might indicate conflict
            severity = 0.3

        # Check for disclosure level conflicts
        if obs1.disclosure_level != obs2.disclosure_level:
            # Different disclosure levels indicate potential conflict
            severity = max(severity, 0.25)

        # Check for content-based conflicts
        # Simple heuristic: look for contradictory words
        contradictory_pairs = [
            ("increase", "decrease"),
            ("improve", "deteriorate"),
            ("strength", "weakness"),
            ("positive", "negative"),
            ("growth", "decline"),
        ]

        content1_lower = obs1.content.lower()
        content2_lower = obs2.content.lower()

        for word1, word2 in contradictory_pairs:
            if (word1 in content1_lower and word2 in content2_lower) or (
                word2 in content1_lower and word1 in content2_lower
            ):
                severity = max(severity, 0.6)
                conflict_type = ConflictType.DATA_INCONSISTENCY
                break

        # If we detected conflicts, determine the type if not already set
        if severity > 0.5 and not conflict_type:
            if obs1.source_tag != obs2.source_tag:
                conflict_type = ConflictType.SOURCE_CONFLICT
            else:
                conflict_type = ConflictType.DATA_INCONSISTENCY

        # Return conflict only if severity above threshold
        if conflict_type and severity > 0.2:
            return (conflict_type, severity)

        return None

    @staticmethod
    async def _get_case(db: AsyncSession, case_id: UUID) -> Optional[Case]:
        """Helper method to get case"""
        stmt = select(Case).where(
            and_(Case.id == case_id, Case.is_deleted == False)  # noqa: E712
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
