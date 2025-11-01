"""User service - business logic for user management"""

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import User
from app.models.schemas import UserCreate, UserResponse, UserRole
from app.core.security import AuthService
from app.core.errors import ValidationException, NotFoundException, ConflictException


class UserService:
    """User management service"""

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
    ) -> User:
        """
        Create a new user account.

        **Parameters**:
        - db: Database session
        - user_data: User creation data (email, full_name, password, role)

        **Returns**:
        - Created User object

        **Errors**:
        - ValidationException: Invalid email or weak password
        - ConflictException: User already exists with this email
        """
        # Validate email format
        if not user_data.email or "@" not in user_data.email:
            raise ValidationException("Invalid email address")

        # Validate password strength
        if len(user_data.password) < 8:
            raise ValidationException("Password must be at least 8 characters")

        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ConflictException(f"User with email {user_data.email} already exists")

        # Hash password
        hashed_password = AuthService.hash_password(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        """
        Get user by email address.

        **Parameters**:
        - db: Database session
        - email: User email address

        **Returns**:
        - User object if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[User]:
        """
        Get user by ID.

        **Parameters**:
        - db: Database session
        - user_id: User ID

        **Returns**:
        - User object if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate user with email and password.

        **Parameters**:
        - db: Database session
        - email: User email
        - password: Plain text password

        **Returns**:
        - User object if authentication successful, None otherwise
        """
        user = await UserService.get_user_by_email(db, email)

        if not user or not user.is_active:
            return None

        # Verify password
        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        **kwargs,
    ) -> Optional[User]:
        """
        Update user information.

        **Parameters**:
        - db: Database session
        - user_id: User ID
        - kwargs: Fields to update (full_name, role, etc.)

        **Returns**:
        - Updated User object if found, None otherwise
        """
        user = await UserService.get_user_by_id(db, user_id)

        if not user:
            return None

        # Update fields
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def deactivate_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[User]:
        """
        Deactivate user account (soft delete).

        **Parameters**:
        - db: Database session
        - user_id: User ID

        **Returns**:
        - Updated User object if found, None otherwise
        """
        return await UserService.update_user(db, user_id, is_active=False)

    @staticmethod
    async def get_users_by_role(
        db: AsyncSession,
        role: UserRole,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[User], int]:
        """
        Get all users with a specific role.

        **Parameters**:
        - db: Database session
        - role: User role to filter by
        - skip: Number of records to skip
        - limit: Number of records to return

        **Returns**:
        - Tuple of (users list, total count)
        """
        # Get total count
        count_stmt = select(User).where(User.role == role)
        count_result = await db.execute(count_stmt)
        total = len(count_result.fetchall())

        # Get paginated results
        stmt = (
            select(User)
            .where(User.role == role)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        return users, total

    @staticmethod
    async def verify_user_exists(
        db: AsyncSession,
        user_id: UUID,
    ) -> bool:
        """
        Check if user exists.

        **Parameters**:
        - db: Database session
        - user_id: User ID

        **Returns**:
        - True if user exists and is active, False otherwise
        """
        user = await UserService.get_user_by_id(db, user_id)
        return user is not None and user.is_active
