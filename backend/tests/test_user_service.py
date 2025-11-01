"""Unit tests for UserService"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import UserRole, UserCreate
from app.services.user_service import UserService
from app.core.errors import ConflictException, ValidationException


class TestUserServiceCreate:
    """Tests for create_user method"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, test_db: AsyncSession):
        """Test successful user creation"""
        user_data = UserCreate(
            email="newuser@test.com",
            full_name="New User",
            password="ValidPassword123!",
            role=UserRole.ANALYST,
        )
        user = await UserService.create_user(test_db, user_data)

        assert user is not None
        assert user.email == "newuser@test.com"
        assert user.full_name == "New User"
        assert user.role == UserRole.ANALYST
        assert user.is_active is True
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test creation fails with duplicate email"""
        user_data = UserCreate(
            email="analyst@test.com",  # Same as test_user_analyst
            full_name="Another Analyst",
            password="ValidPassword123!",
            role=UserRole.ANALYST,
        )
        with pytest.raises(ConflictException):
            await UserService.create_user(test_db, user_data)

    @pytest.mark.asyncio
    async def test_create_user_invalid_password_too_short(self, test_db: AsyncSession):
        """Test creation fails with password too short"""
        user_data = UserCreate(
            email="newuser@test.com",
            full_name="New User",
            password="short",  # Too short
            role=UserRole.ANALYST,
        )
        with pytest.raises(ValidationException):
            await UserService.create_user(test_db, user_data)

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, test_db: AsyncSession):
        """Test creation fails with invalid email"""
        user_data = UserCreate(
            email="invalidemail",  # No @ symbol
            full_name="New User",
            password="ValidPassword123!",
            role=UserRole.ANALYST,
        )
        with pytest.raises(ValidationException):
            await UserService.create_user(test_db, user_data)

    @pytest.mark.asyncio
    async def test_create_user_all_roles(self, test_db: AsyncSession):
        """Test user creation with all role types"""
        roles = [
            UserRole.ANALYST,
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        for idx, role in enumerate(roles):
            user_data = UserCreate(
                email=f"user{idx}@test.com",
                full_name=f"Test User {role.value}",
                password="ValidPassword123!",
                role=role,
            )
            user = await UserService.create_user(test_db, user_data)
            assert user.role == role


class TestUserServiceAuthenticate:
    """Tests for authenticate_user method"""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test successful user authentication"""
        user = await UserService.authenticate_user(
            test_db, "analyst@test.com", "testpass123"
        )

        assert user is not None
        assert user.email == "analyst@test.com"
        assert user.id == test_user_analyst.id

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, test_db: AsyncSession):
        """Test authentication fails with non-existent email"""
        user = await UserService.authenticate_user(
            test_db, "nonexistent@test.com", "testpass123"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test authentication fails with incorrect password"""
        user = await UserService.authenticate_user(
            test_db, "analyst@test.com", "wrongpassword"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_account(self, test_db: AsyncSession):
        """Test authentication fails for inactive user"""
        from app.models.database import User
        from app.core.security import AuthService

        # Create inactive user
        inactive_user = User(
            id=uuid4(),
            email="inactive@test.com",
            full_name="Inactive User",
            hashed_password=AuthService.hash_password("testpass123"),
            role=UserRole.ANALYST,
            is_active=False,
        )
        test_db.add(inactive_user)
        await test_db.commit()

        user = await UserService.authenticate_user(
            test_db, "inactive@test.com", "testpass123"
        )

        assert user is None


class TestUserServiceGetById:
    """Tests for get_user_by_id method"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test successful user retrieval by ID"""
        user = await UserService.get_user_by_id(test_db, test_user_analyst.id)

        assert user is not None
        assert user.id == test_user_analyst.id
        assert user.email == "analyst@test.com"

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_db: AsyncSession):
        """Test get_user_by_id returns None for non-existent user"""
        non_existent_id = uuid4()
        user = await UserService.get_user_by_id(test_db, non_existent_id)

        assert user is None


class TestUserServiceGetByEmail:
    """Tests for get_user_by_email method"""

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test successful user retrieval by email"""
        user = await UserService.get_user_by_email(test_db, "analyst@test.com")

        assert user is not None
        assert user.email == "analyst@test.com"
        assert user.id == test_user_analyst.id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, test_db: AsyncSession):
        """Test get_user_by_email returns None for non-existent email"""
        user = await UserService.get_user_by_email(
            test_db, "nonexistent@test.com"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_insensitive(self, test_db: AsyncSession):
        """Test get_user_by_email is case-insensitive"""
        user = await UserService.get_user_by_email(test_db, "ANALYST@TEST.COM")

        assert user is not None
        assert user.email == "analyst@test.com"


class TestUserServiceVerifyExists:
    """Tests for verify_user_exists method"""

    @pytest.mark.asyncio
    async def test_verify_user_exists_true(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test verify_user_exists returns True for existing user"""
        exists = await UserService.verify_user_exists(
            test_db, "analyst@test.com"
        )

        assert exists is True

    @pytest.mark.asyncio
    async def test_verify_user_exists_false(self, test_db: AsyncSession):
        """Test verify_user_exists returns False for non-existent user"""
        exists = await UserService.verify_user_exists(
            test_db, "nonexistent@test.com"
        )

        assert exists is False


class TestUserServiceUpdate:
    """Tests for update_user method"""

    @pytest.mark.asyncio
    async def test_update_user_full_name(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test updating user's full name"""
        updated_user = await UserService.update_user(
            test_db, test_user_analyst.id, full_name="Updated Name"
        )

        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "analyst@test.com"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_user_email(self, test_db: AsyncSession, test_user_analyst):
        """Test updating user's email"""
        updated_user = await UserService.update_user(
            test_db, test_user_analyst.id, email="newemail@test.com"
        )

        assert updated_user.email == "newemail@test.com"

    @pytest.mark.asyncio
    async def test_update_user_multiple_fields(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test updating multiple user fields"""
        updated_user = await UserService.update_user(
            test_db,
            test_user_analyst.id,
            full_name="New Name",
            email="newemail@test.com",
        )

        assert updated_user.full_name == "New Name"
        assert updated_user.email == "newemail@test.com"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, test_db: AsyncSession):
        """Test update_user raises exception for non-existent user"""
        from app.core.errors import NotFoundException

        non_existent_id = uuid4()
        with pytest.raises(NotFoundException):
            await UserService.update_user(
                test_db, non_existent_id, full_name="New Name"
            )


class TestUserServiceDeactivate:
    """Tests for deactivate_user method"""

    @pytest.mark.asyncio
    async def test_deactivate_user_success(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test successful user deactivation"""
        deactivated_user = await UserService.deactivate_user(
            test_db, test_user_analyst.id
        )

        assert deactivated_user.is_active is False
        assert deactivated_user.email == "analyst@test.com"  # Unchanged

    @pytest.mark.asyncio
    async def test_deactivate_user_prevents_authentication(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test deactivated user cannot authenticate"""
        await UserService.deactivate_user(test_db, test_user_analyst.id)

        user = await UserService.authenticate_user(
            test_db, "analyst@test.com", "testpass123"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_deactivate_user_not_found(self, test_db: AsyncSession):
        """Test deactivate_user raises exception for non-existent user"""
        from app.core.errors import NotFoundException

        non_existent_id = uuid4()
        with pytest.raises(NotFoundException):
            await UserService.deactivate_user(test_db, non_existent_id)


class TestUserServiceGetByRole:
    """Tests for get_users_by_role method"""

    @pytest.mark.asyncio
    async def test_get_users_by_role_analyst(
        self, test_db: AsyncSession, test_user_analyst
    ):
        """Test retrieving users by ANALYST role"""
        users = await UserService.get_users_by_role(test_db, UserRole.ANALYST)

        assert len(users) >= 1
        assert any(u.id == test_user_analyst.id for u in users)
        assert all(u.role == UserRole.ANALYST for u in users)

    @pytest.mark.asyncio
    async def test_get_users_by_role_multiple_roles(self, test_db: AsyncSession):
        """Test retrieving users of different roles"""
        # Create users with different roles
        await UserService.create_user(
            test_db,
            email="lead@test.com",
            full_name="Test Lead",
            password="ValidPassword123!",
            role=UserRole.LEAD_PARTNER,
        )

        analysts = await UserService.get_users_by_role(test_db, UserRole.ANALYST)
        leads = await UserService.get_users_by_role(test_db, UserRole.LEAD_PARTNER)

        assert len(analysts) >= 1
        assert len(leads) >= 1
        assert all(u.role == UserRole.ANALYST for u in analysts)
        assert all(u.role == UserRole.LEAD_PARTNER for u in leads)

    @pytest.mark.asyncio
    async def test_get_users_by_role_empty(self, test_db: AsyncSession):
        """Test retrieving users of role with no members"""
        # Create only analyst user, try to get IC_MEMBER users
        users = await UserService.get_users_by_role(test_db, UserRole.IC_MEMBER)

        assert isinstance(users, list)


class TestUserServiceIntegration:
    """Integration tests for UserService"""

    @pytest.mark.asyncio
    async def test_full_user_lifecycle(self, test_db: AsyncSession):
        """Test complete user lifecycle: create -> get -> update -> deactivate"""
        # Create user
        user = await UserService.create_user(
            test_db,
            email="lifecycle@test.com",
            full_name="Lifecycle User",
            password="ValidPassword123!",
            role=UserRole.ANALYST,
        )
        user_id = user.id

        # Get user by ID
        retrieved = await UserService.get_user_by_id(test_db, user_id)
        assert retrieved.email == "lifecycle@test.com"

        # Get user by email
        by_email = await UserService.get_user_by_email(test_db, "lifecycle@test.com")
        assert by_email.id == user_id

        # Authenticate
        authenticated = await UserService.authenticate_user(
            test_db, "lifecycle@test.com", "ValidPassword123!"
        )
        assert authenticated.id == user_id

        # Update
        updated = await UserService.update_user(
            test_db, user_id, full_name="Updated Lifecycle User"
        )
        assert updated.full_name == "Updated Lifecycle User"

        # Deactivate
        deactivated = await UserService.deactivate_user(test_db, user_id)
        assert deactivated.is_active is False

        # Verify cannot authenticate after deactivation
        post_deactivation = await UserService.authenticate_user(
            test_db, "lifecycle@test.com", "ValidPassword123!"
        )
        assert post_deactivation is None
