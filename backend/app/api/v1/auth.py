"""Authentication API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import AuthService, get_current_user
from app.core.errors import AuthenticationException, ValidationException, ConflictException, NotFoundException
from app.models.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    CurrentUserResponse,
    UserCreate,
    UserResponse,
)
from app.services.user_service import UserService


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    **Parameters:**
    - **user_data**: User registration data (email, full_name, password, role)

    **Returns:**
    - User response with ID and metadata

    **Errors:**
    - 400: Validation error (invalid email, weak password)
    - 409: User already exists with this email
    - 500: Internal server error
    """
    try:
        # Create user via service
        user = await UserService.create_user(db, user_data)

        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
        )

    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    User login endpoint.

    **Parameters:**
    - **credentials**: Login credentials (email, password)

    **Returns:**
    - Access token, refresh token, and expiry time

    **Errors:**
    - 401: Invalid credentials
    - 500: Internal server error
    """
    # Authenticate user
    user = await UserService.authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate tokens
    access_token = AuthService.create_access_token(str(user.id), user.role.value)
    refresh_token = AuthService.create_refresh_token(str(user.id), user.role.value)

    # Get token expiry time
    from app.config import get_settings
    settings = get_settings()
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    **Parameters:**
    - **request**: Refresh token request

    **Returns:**
    - New access token and refresh token

    **Errors:**
    - 401: Invalid or expired refresh token
    - 500: Internal server error
    """
    try:
        # Verify refresh token
        payload = AuthService.verify_token(request.refresh_token)

        # Extract user_id and role
        user_id = payload.get("sub")
        role = payload.get("role")
        token_type = payload.get("type")

        # Verify it's a refresh token
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Generate new tokens
        access_token = AuthService.create_access_token(user_id, role)
        new_refresh_token = AuthService.create_refresh_token(user_id, role)

        # Get token expiry time
        from app.config import get_settings
        settings = get_settings()
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user information.

    **Returns:**
    - Current user details and permissions

    **Errors:**
    - 401: Not authenticated
    - 500: Internal server error
    """
    # Get full user information from database
    from uuid import UUID
    user = await UserService.get_user_by_id(db, UUID(current_user.get("user_id")))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return CurrentUserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        permissions=current_user.get("permissions", []),
    )
