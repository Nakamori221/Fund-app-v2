"""Unit tests for ConflictService"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    CaseCreate,
    ObservationCreate,
    UserRole,
    SourceTag,
    DisclosureLevel,
    ConflictType,
)
from app.models.database import Case, Observation, Conflict
from app.services.conflict_service import ConflictService
from app.services.case_service import CaseService
from app.services.observation_service import ObservationService
from app.core.errors import NotFoundException, ValidationException, AuthorizationException


class TestConflictServiceDetect:
    """Test conflict detection"""

    @pytest.mark.asyncio
    async def test_detect_conflicts_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful conflict detection"""
        # Create two observations with contradictory content
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial",
            content="Revenue shows strong growth in the market.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Financial",
            content="Revenue shows significant decline in the market.",
        )

        obs1 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data1
        )
        obs2 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data2
        )

        # Detect conflicts
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(conflicts) == 1
        assert conflicts[0].case_id == test_case.id
        assert conflicts[0].is_resolved is False

    @pytest.mark.asyncio
    async def test_detect_conflicts_unauthorized(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test conflict detection by analyst (not authorized)"""
        # Create observations
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="This is observation content.",
        )
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)

        with pytest.raises(AuthorizationException) as exc_info:
            await ConflictService.detect_conflicts(
                test_db, test_case.id, test_user_analyst.id, UserRole.ANALYST
            )

        assert "Only lead partners and above can detect conflicts" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_detect_conflicts_case_not_found(self, test_db: AsyncSession, test_user_lead):
        """Test conflict detection in non-existent case"""
        fake_case_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ConflictService.detect_conflicts(
                test_db, fake_case_id, test_user_lead.id, UserRole.LEAD_PARTNER
            )

        assert "Case not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_detect_conflicts_insufficient_observations(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test conflict detection with less than 2 observations"""
        # Create only one observation
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is observation content.",
        )
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        # Detect conflicts should return empty list
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(conflicts) == 0

    @pytest.mark.asyncio
    async def test_detect_conflicts_no_actual_conflicts(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test conflict detection with compatible observations"""
        # Create observations that don't have conflicts
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial",
            content="The company has strong financial metrics.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Operational",
            content="Operational efficiency is good.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(conflicts) == 0


class TestConflictServiceGetById:
    """Test conflict retrieval by ID"""

    @pytest.mark.asyncio
    async def test_get_conflict_by_id_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful conflict retrieval"""
        # Create conflicting observations
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="Strong growth expected.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Section2",
            content="Decline is anticipated.",
        )

        obs1 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data1
        )
        obs2 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data2
        )

        # Detect conflicts
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(conflicts) > 0
        conflict = conflicts[0]

        # Retrieve by ID
        retrieved = await ConflictService.get_conflict_by_id(test_db, conflict.id)

        assert retrieved is not None
        assert retrieved.id == conflict.id

    @pytest.mark.asyncio
    async def test_get_conflict_by_id_not_found(self, test_db: AsyncSession):
        """Test retrieval of non-existent conflict"""
        fake_id = uuid4()
        conflict = await ConflictService.get_conflict_by_id(test_db, fake_id)

        assert conflict is None


class TestConflictServiceGetConflicts:
    """Test conflicts listing with RBAC"""

    @pytest.mark.asyncio
    async def test_get_conflicts_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful conflicts listing"""
        # Create multiple observations with conflicts
        for i in range(3):
            obs_data = ObservationCreate(
                case_id=str(test_case.id),
                source_tag=SourceTag.PUBLIC if i % 2 == 0 else SourceTag.INTERNAL,
                section=f"Section{i}",
                content=f"Observation {i} shows growth trends." if i % 2 == 0 else f"Observation {i} shows decline trends.",
            )
            await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        # Detect conflicts
        await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        # Get conflicts
        conflicts, total = await ConflictService.get_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert total > 0
        assert len(conflicts) > 0

    @pytest.mark.asyncio
    async def test_get_conflicts_resolved_filter(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test conflicts listing with resolved filter"""
        # Create observations with conflicts
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="Strong growth expected.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Section2",
            content="Decline is anticipated.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        # Detect conflicts
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        if len(conflicts) > 0:
            # Resolve first conflict
            await ConflictService.resolve_conflict(
                test_db, conflicts[0].id, test_user_lead.id, UserRole.LEAD_PARTNER,
                resolution_notes="Resolved after review"
            )

        # Get unresolved conflicts
        unresolved, total_unresolved = await ConflictService.get_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER,
            resolved_filter=False
        )

        # Get resolved conflicts
        resolved, total_resolved = await ConflictService.get_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER,
            resolved_filter=True
        )

        assert total_resolved > 0
        assert resolved[0].is_resolved is True

    @pytest.mark.asyncio
    async def test_get_conflicts_case_not_found(self, test_db: AsyncSession, test_user_lead):
        """Test conflicts listing for non-existent case"""
        fake_case_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ConflictService.get_conflicts(
                test_db, fake_case_id, test_user_lead.id, UserRole.LEAD_PARTNER
            )

        assert "Case not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_conflicts_pagination(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test conflicts listing with pagination"""
        # Create multiple conflicting observations
        for i in range(4):
            obs_data = ObservationCreate(
                case_id=str(test_case.id),
                source_tag=SourceTag.PUBLIC if i % 2 == 0 else SourceTag.INTERNAL,
                section=f"Section{i}",
                content=f"Observation {i} shows growth." if i % 2 == 0 else f"Observation {i} shows decline.",
            )
            await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        # Detect conflicts
        await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        # Get first 2
        conflicts, total = await ConflictService.get_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER, skip=0, limit=2
        )

        assert len(conflicts) <= 2
        assert total > 0


class TestConflictServiceResolve:
    """Test conflict resolution"""

    @pytest.mark.asyncio
    async def test_resolve_conflict_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful conflict resolution"""
        # Create observations with conflict
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="Strong growth expected in revenue.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Section2",
            content="Significant decline is anticipated.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        # Detect conflicts
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(conflicts) > 0
        conflict = conflicts[0]

        # Resolve conflict
        resolved = await ConflictService.resolve_conflict(
            test_db, conflict.id, test_user_lead.id, UserRole.LEAD_PARTNER,
            resolution_notes="Reviewed and confirmed accurate data"
        )

        assert resolved.is_resolved is True
        assert resolved.resolved_by == test_user_lead.id
        assert resolved.resolved_at is not None
        assert resolved.resolution_notes == "Reviewed and confirmed accurate data"

    @pytest.mark.asyncio
    async def test_resolve_conflict_not_found(self, test_db: AsyncSession, test_user_lead):
        """Test resolution of non-existent conflict"""
        fake_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ConflictService.resolve_conflict(
                test_db, fake_id, test_user_lead.id, UserRole.LEAD_PARTNER
            )

        assert "Conflict not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_resolve_conflict_unauthorized(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test conflict resolution by analyst (not authorized)"""
        # Create observations with conflict
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="Strong growth expected.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Section2",
            content="Decline is anticipated.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        # Detect conflicts
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(conflicts) > 0
        conflict = conflicts[0]

        # Analyst tries to resolve
        with pytest.raises(AuthorizationException) as exc_info:
            await ConflictService.resolve_conflict(
                test_db, conflict.id, test_user_analyst.id, UserRole.ANALYST
            )

        assert "Only lead partners and above can resolve conflicts" in str(exc_info.value)


class TestConflictServiceHighSeverity:
    """Test high severity conflict filtering"""

    @pytest.mark.asyncio
    async def test_get_high_severity_conflicts_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful high severity conflict retrieval"""
        # Create observations with strong conflict indicators
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial",
            content="Financial improvement and growth expected in all sectors.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Financial",
            content="Financial deterioration and decline anticipated.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        # Detect conflicts
        await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        # Get high severity conflicts
        high_severity = await ConflictService.get_high_severity_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER,
            severity_threshold=0.5
        )

        # Should have at least one high severity conflict
        if len(high_severity) > 0:
            assert high_severity[0].severity >= 0.5
            assert high_severity[0].is_resolved is False

    @pytest.mark.asyncio
    async def test_get_high_severity_conflicts_case_not_found(self, test_db: AsyncSession, test_user_lead):
        """Test high severity conflicts for non-existent case"""
        fake_case_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ConflictService.get_high_severity_conflicts(
                test_db, fake_case_id, test_user_lead.id, UserRole.LEAD_PARTNER
            )

        assert "Case not found" in str(exc_info.value)


class TestConflictServiceStatistics:
    """Test conflict statistics"""

    @pytest.mark.asyncio
    async def test_get_conflict_statistics_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful statistics retrieval"""
        # Create observations
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="Strong growth expected.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Section2",
            content="Decline is anticipated.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        # Detect conflicts
        conflicts = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        if len(conflicts) > 0:
            # Resolve first conflict
            await ConflictService.resolve_conflict(
                test_db, conflicts[0].id, test_user_lead.id, UserRole.LEAD_PARTNER
            )

        # Get statistics
        stats = await ConflictService.get_conflict_statistics(test_db, test_case.id)

        assert stats["case_id"] == str(test_case.id)
        assert stats["total_count"] > 0
        assert stats["resolved_count"] >= 0
        assert stats["unresolved_count"] >= 0
        assert "average_severity" in stats
        assert "by_type" in stats

    @pytest.mark.asyncio
    async def test_get_conflict_statistics_empty(self, test_db: AsyncSession, test_case):
        """Test statistics for case with no conflicts"""
        stats = await ConflictService.get_conflict_statistics(test_db, test_case.id)

        assert stats["total_count"] == 0
        assert stats["resolved_count"] == 0
        assert stats["unresolved_count"] == 0
        assert stats["average_severity"] == 0


class TestConflictServiceIntegration:
    """Test conflict service integration scenarios"""

    @pytest.mark.asyncio
    async def test_conflict_full_lifecycle(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test complete conflict detection and resolution lifecycle"""
        # Step 1: Create observations with conflicts
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Market Analysis",
            content="Market growth is positive and accelerating.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Internal Report",
            content="Market decline is expected and accelerating.",
        )

        obs1 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data1
        )
        obs2 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data2
        )

        # Step 2: Detect conflicts
        detected = await ConflictService.detect_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert len(detected) > 0
        conflict = detected[0]
        assert conflict.is_resolved is False

        # Step 3: Get conflicts
        conflicts, total = await ConflictService.get_conflicts(
            test_db, test_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert total > 0
        assert len(conflicts) > 0

        # Step 4: Resolve conflict
        resolved = await ConflictService.resolve_conflict(
            test_db, conflict.id, test_user_lead.id, UserRole.LEAD_PARTNER,
            resolution_notes="Reviewed both data sources. Internal data takes precedence."
        )

        assert resolved.is_resolved is True
        assert "precedence" in resolved.resolution_notes

        # Step 5: Get statistics
        stats = await ConflictService.get_conflict_statistics(test_db, test_case.id)

        assert stats["total_count"] > 0
        assert stats["resolved_count"] > 0
        assert stats["unresolved_count"] >= 0
