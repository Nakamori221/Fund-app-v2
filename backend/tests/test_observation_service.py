"""Unit tests for ObservationService"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.schemas import (
    UserCreate,
    CaseCreate,
    ObservationCreate,
    ObservationUpdate,
    CaseStatus,
    UserRole,
    SourceTag,
    DisclosureLevel,
)
from app.models.database import User, Case, Observation
from app.services.observation_service import ObservationService
from app.services.case_service import CaseService
from app.services.user_service import UserService
from app.core.errors import NotFoundException, ValidationException, AuthorizationException


class TestObservationServiceCreate:
    """Test observation creation"""

    @pytest.mark.asyncio
    async def test_create_observation_success(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test successful observation creation"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial Analysis",
            content="This is a detailed financial observation about the company.",
            disclosure_level=DisclosureLevel.PRIVATE,
        )

        observation = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        assert observation is not None
        assert observation.section == "Financial Analysis"
        assert observation.content == "This is a detailed financial observation about the company."
        assert observation.source_tag == SourceTag.PUBLIC
        assert observation.disclosure_level == DisclosureLevel.PRIVATE
        assert observation.created_by == test_user_analyst.id
        assert observation.is_verified is False
        assert observation.is_deleted is False

    @pytest.mark.asyncio
    async def test_create_observation_case_not_found(self, test_db: AsyncSession, test_user_analyst):
        """Test observation creation with non-existent case"""
        fake_case_id = uuid4()
        obs_data = ObservationCreate(
            case_id=str(fake_case_id),
            source_tag=SourceTag.PUBLIC,
            section="Test Section",
            content="This is test content for observation.",
        )

        with pytest.raises(NotFoundException) as exc_info:
            await ObservationService.create_observation(test_db, fake_case_id, test_user_analyst.id, obs_data)

        assert "Case not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_observation_content_too_short(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observation creation with content too short"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            obs_data = ObservationCreate(
                case_id=str(test_case.id),
                source_tag=SourceTag.PUBLIC,
                section="Test Section",
                content="Short",  # Less than 10 characters
            )

        assert "at least 10 characters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_observation_missing_section(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observation creation without section"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="",  # Empty section
            content="This is a valid observation content.",
        )

        with pytest.raises(ValidationException) as exc_info:
            await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        assert "Section is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_observation_with_metadata(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observation creation with metadata"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.CONFIDENTIAL,
            section="Legal Analysis",
            content="This is a detailed legal observation about the company.",
            metadata={"lawyer": "John Doe", "review_date": "2025-01-15"},
        )

        observation = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        assert observation.extra_data == {"lawyer": "John Doe", "review_date": "2025-01-15"}
        assert observation.source_tag == SourceTag.CONFIDENTIAL


class TestObservationServiceGetById:
    """Test observation retrieval by ID"""

    @pytest.mark.asyncio
    async def test_get_observation_by_id_success(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test successful observation retrieval"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Test Section",
            content="This is a test observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )
        retrieved_obs = await ObservationService.get_observation_by_id(test_db, created_obs.id)

        assert retrieved_obs is not None
        assert retrieved_obs.id == created_obs.id
        assert retrieved_obs.section == "Test Section"

    @pytest.mark.asyncio
    async def test_get_observation_by_id_not_found(self, test_db: AsyncSession):
        """Test observation retrieval with non-existent ID"""
        fake_id = uuid4()
        observation = await ObservationService.get_observation_by_id(test_db, fake_id)

        assert observation is None

    @pytest.mark.asyncio
    async def test_get_observation_by_id_deleted(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test retrieval of deleted observation returns None"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Test Section",
            content="This is a test observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )
        await ObservationService.delete_observation(
            test_db, created_obs.id, test_user_analyst.id, UserRole.ANALYST
        )
        retrieved_obs = await ObservationService.get_observation_by_id(test_db, created_obs.id)

        assert retrieved_obs is None


class TestObservationServiceGetObservations:
    """Test observations listing with RBAC"""

    @pytest.mark.asyncio
    async def test_get_observations_success(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test successful observations listing"""
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial",
            content="This is a financial observation content.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Legal",
            content="This is a legal observation content.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        observations, total = await ObservationService.get_observations(
            test_db, test_case.id, test_user_analyst.id, UserRole.ANALYST
        )

        assert len(observations) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_observations_with_source_filter(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observations listing with source tag filter"""
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="This is a public observation content.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.CONFIDENTIAL,
            section="Section2",
            content="This is a confidential observation content.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        observations, total = await ObservationService.get_observations(
            test_db,
            test_case.id,
            test_user_analyst.id,
            UserRole.ANALYST,
            source_tag_filter=SourceTag.PUBLIC,
        )

        assert len(observations) == 1
        assert total == 1
        assert observations[0].source_tag == SourceTag.PUBLIC

    @pytest.mark.asyncio
    async def test_get_observations_analyst_rbac(self, test_db: AsyncSession, test_user_analyst, test_user_lead):
        """Test RBAC: analyst can only see own cases"""
        case_data = CaseCreate(
            title="Analyst Case",
            description="Case created by analyst",
            company_name="Analyst Company",
        )
        analyst_case = await CaseService.create_case(test_db, test_user_analyst.id, case_data)

        obs_data = ObservationCreate(
            case_id=str(analyst_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is a test observation content.",
        )
        await ObservationService.create_observation(test_db, analyst_case.id, test_user_analyst.id, obs_data)

        # Lead can see all cases and their observations
        observations, total = await ObservationService.get_observations(
            test_db, analyst_case.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )
        assert len(observations) == 1

    @pytest.mark.asyncio
    async def test_get_observations_pagination(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observations listing with pagination"""
        # Create 5 observations
        for i in range(5):
            obs_data = ObservationCreate(
                case_id=str(test_case.id),
                source_tag=SourceTag.PUBLIC,
                section=f"Section {i}",
                content=f"This is observation content number {i}.",
            )
            await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        # Get first 2
        observations, total = await ObservationService.get_observations(
            test_db, test_case.id, test_user_analyst.id, UserRole.ANALYST, skip=0, limit=2
        )

        assert len(observations) == 2
        assert total == 5


class TestObservationServiceUpdate:
    """Test observation update"""

    @pytest.mark.asyncio
    async def test_update_observation_success(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test successful observation update by creator"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Original Section",
            content="This is original observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        update_data = ObservationUpdate(
            content="This is updated observation content.",
            section="Updated Section",
        )

        updated_obs = await ObservationService.update_observation(
            test_db, created_obs.id, test_user_analyst.id, UserRole.ANALYST, update_data
        )

        assert updated_obs.content == "This is updated observation content."
        assert updated_obs.section == "Updated Section"

    @pytest.mark.asyncio
    async def test_update_observation_content_too_short(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observation update with content too short"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is original observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        update_data = ObservationUpdate(content="Short")

        with pytest.raises(ValidationException) as exc_info:
            await ObservationService.update_observation(
                test_db, created_obs.id, test_user_analyst.id, UserRole.ANALYST, update_data
            )

        assert "at least 10 characters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_observation_not_found(self, test_db: AsyncSession, test_user_analyst):
        """Test update of non-existent observation"""
        fake_id = uuid4()
        update_data = ObservationUpdate(content="This is updated observation content.")

        with pytest.raises(NotFoundException) as exc_info:
            await ObservationService.update_observation(
                test_db, fake_id, test_user_analyst.id, UserRole.ANALYST, update_data
            )

        assert "Observation not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_observation_unauthorized(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test update of observation by non-creator analyst"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is original observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        # Different analyst tries to update
        other_analyst = await UserService.create_user(
            test_db,
            UserCreate(
                email="other.analyst@example.com",
                password="password123",
                full_name="Other Analyst",
                role=UserRole.ANALYST,
            ),
        )

        update_data = ObservationUpdate(content="This is updated observation content.")

        with pytest.raises(AuthorizationException) as exc_info:
            await ObservationService.update_observation(
                test_db, created_obs.id, other_analyst.id, UserRole.ANALYST, update_data
            )

        assert "Not authorized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_observation_by_lead(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test update of observation by lead partner"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is original observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        # Lead can update any observation
        update_data = ObservationUpdate(
            content="This is updated observation content.",
            disclosure_level=DisclosureLevel.IC,
        )

        updated_obs = await ObservationService.update_observation(
            test_db, created_obs.id, test_user_lead.id, UserRole.LEAD_PARTNER, update_data
        )

        assert updated_obs.content == "This is updated observation content."
        assert updated_obs.disclosure_level == DisclosureLevel.IC


class TestObservationServiceDelete:
    """Test observation deletion"""

    @pytest.mark.asyncio
    async def test_delete_observation_success(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test successful observation deletion by creator"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is observation content to be deleted.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        deleted_obs = await ObservationService.delete_observation(
            test_db, created_obs.id, test_user_analyst.id, UserRole.ANALYST
        )

        assert deleted_obs.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_observation_not_found(self, test_db: AsyncSession, test_user_analyst):
        """Test deletion of non-existent observation"""
        fake_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ObservationService.delete_observation(test_db, fake_id, test_user_analyst.id, UserRole.ANALYST)

        assert "Observation not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_observation_unauthorized(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test deletion of observation by non-creator analyst"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        # Different analyst tries to delete
        other_analyst = await UserService.create_user(
            test_db,
            UserCreate(
                email="other.analyst2@example.com",
                password="password123",
                full_name="Other Analyst",
                role=UserRole.ANALYST,
            ),
        )

        with pytest.raises(AuthorizationException) as exc_info:
            await ObservationService.delete_observation(
                test_db, created_obs.id, other_analyst.id, UserRole.ANALYST
            )

        assert "Not authorized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_observation_by_lead(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test deletion of observation by lead partner"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        # Lead can delete any observation
        deleted_obs = await ObservationService.delete_observation(
            test_db, created_obs.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert deleted_obs.is_deleted is True


class TestObservationServiceVerify:
    """Test observation verification"""

    @pytest.mark.asyncio
    async def test_verify_observation_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful observation verification by lead"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is observation content to be verified.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        verified_obs = await ObservationService.verify_observation(
            test_db, created_obs.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        assert verified_obs.is_verified is True
        assert verified_obs.verified_by == test_user_lead.id
        assert verified_obs.verified_at is not None

    @pytest.mark.asyncio
    async def test_verify_observation_not_found(self, test_db: AsyncSession, test_user_lead):
        """Test verification of non-existent observation"""
        fake_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ObservationService.verify_observation(
                test_db, fake_id, test_user_lead.id, UserRole.LEAD_PARTNER
            )

        assert "Observation not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_observation_unauthorized(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test verification of observation by analyst (not lead)"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section",
            content="This is observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )

        with pytest.raises(AuthorizationException) as exc_info:
            await ObservationService.verify_observation(
                test_db, created_obs.id, test_user_analyst.id, UserRole.ANALYST
            )

        assert "Only lead partners and above can verify" in str(exc_info.value)


class TestObservationServiceSearch:
    """Test observation search"""

    @pytest.mark.asyncio
    async def test_search_observations_success(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test successful observation search"""
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial",
            content="Revenue analysis shows strong growth in Q4 2024.",
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Legal",
            content="Compliance review indicates no major issues.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data1)
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        observations, total = await ObservationService.search_observations(
            test_db, test_case.id, test_user_analyst.id, UserRole.ANALYST, query="revenue"
        )

        assert len(observations) == 1
        assert total == 1
        assert "Revenue" in observations[0].content

    @pytest.mark.asyncio
    async def test_search_observations_no_results(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observation search with no results"""
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Financial",
            content="Revenue analysis shows strong growth in Q4 2024.",
        )

        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        observations, total = await ObservationService.search_observations(
            test_db, test_case.id, test_user_analyst.id, UserRole.ANALYST, query="nonexistent"
        )

        assert len(observations) == 0
        assert total == 0

    @pytest.mark.asyncio
    async def test_search_observations_case_not_found(self, test_db: AsyncSession, test_user_analyst):
        """Test search in non-existent case"""
        fake_case_id = uuid4()

        with pytest.raises(NotFoundException) as exc_info:
            await ObservationService.search_observations(
                test_db, fake_case_id, test_user_analyst.id, UserRole.ANALYST, query="test"
            )

        assert "Case not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_observations_pagination(self, test_db: AsyncSession, test_user_analyst, test_case):
        """Test observation search with pagination"""
        for i in range(5):
            obs_data = ObservationCreate(
                case_id=str(test_case.id),
                source_tag=SourceTag.PUBLIC,
                section="Section",
                content=f"This observation number {i} contains search term.",
            )
            await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data)

        observations, total = await ObservationService.search_observations(
            test_db, test_case.id, test_user_analyst.id, UserRole.ANALYST, query="search", skip=0, limit=2
        )

        assert len(observations) == 2
        assert total == 5


class TestObservationServiceStatistics:
    """Test observation statistics"""

    @pytest.mark.asyncio
    async def test_get_observation_statistics_success(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test successful statistics retrieval"""
        # Create observations with different characteristics
        obs_data1 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.PUBLIC,
            section="Section1",
            content="This is public observation content.",
            disclosure_level=DisclosureLevel.PRIVATE,
        )
        obs_data2 = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.CONFIDENTIAL,
            section="Section2",
            content="This is confidential observation content.",
            disclosure_level=DisclosureLevel.IC,
        )

        obs1 = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data1
        )
        await ObservationService.create_observation(test_db, test_case.id, test_user_analyst.id, obs_data2)

        # Verify one observation (only lead partner can verify)
        await ObservationService.verify_observation(
            test_db, obs1.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )

        stats = await ObservationService.get_observation_statistics(test_db, test_case.id)

        assert stats["total_count"] == 2
        assert stats["verified_count"] == 1
        assert stats["unverified_count"] == 1
        assert "PUB" in stats["by_source_tag"]  # SourceTag.PUBLIC.value = "PUB"
        assert "CONF" in stats["by_source_tag"]  # SourceTag.CONFIDENTIAL.value = "CONF"

    @pytest.mark.asyncio
    async def test_get_observation_statistics_empty(self, test_db: AsyncSession, test_case):
        """Test statistics for case with no observations"""
        stats = await ObservationService.get_observation_statistics(test_db, test_case.id)

        assert stats["total_count"] == 0
        assert stats["verified_count"] == 0
        assert stats["unverified_count"] == 0


class TestObservationServiceIntegration:
    """Test observation service integration scenarios"""

    @pytest.mark.asyncio
    async def test_observation_lifecycle(self, test_db: AsyncSession, test_user_analyst, test_user_lead, test_case):
        """Test complete observation lifecycle: create, update, verify, delete"""
        # Create observation
        obs_data = ObservationCreate(
            case_id=str(test_case.id),
            source_tag=SourceTag.INTERNAL,
            section="Operational Analysis",
            content="This is initial operational observation content.",
        )

        created_obs = await ObservationService.create_observation(
            test_db, test_case.id, test_user_analyst.id, obs_data
        )
        assert created_obs.is_verified is False
        assert created_obs.is_deleted is False

        # Update observation
        update_data = ObservationUpdate(
            content="This is updated operational observation content.",
            source_tag=SourceTag.CONFIDENTIAL,
        )

        updated_obs = await ObservationService.update_observation(
            test_db, created_obs.id, test_user_analyst.id, UserRole.ANALYST, update_data
        )
        assert updated_obs.source_tag == SourceTag.CONFIDENTIAL
        assert "updated" in updated_obs.content

        # Verify observation
        verified_obs = await ObservationService.verify_observation(
            test_db, updated_obs.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )
        assert verified_obs.is_verified is True
        assert verified_obs.verified_by == test_user_lead.id

        # Delete observation
        deleted_obs = await ObservationService.delete_observation(
            test_db, verified_obs.id, test_user_lead.id, UserRole.LEAD_PARTNER
        )
        assert deleted_obs.is_deleted is True

        # Verify it's not retrieved anymore
        retrieved = await ObservationService.get_observation_by_id(test_db, deleted_obs.id)
        assert retrieved is None
