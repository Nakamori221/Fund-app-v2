"""JWT authentication and security utilities"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import uuid

from app.config import get_settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# HTTPAuthCredentials for type hinting (compatible with newer FastAPI versions)
class HTTPAuthCredentials:
    """HTTP Authentication credentials"""
    def __init__(self, credentials: str):
        self.credentials = credentials


class AuthService:
    """JWT and authentication service"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        user_id: str,
        role: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token"""
        settings = get_settings()

        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {
            "sub": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: str, role: str) -> str:
        """Create JWT refresh token"""
        settings = get_settings()

        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {
            "sub": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        settings = get_settings()

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from e


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials

    try:
        payload = AuthService.verify_token(token)

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
            )

        return {
            "user_id": user_id,
            "role": role,
            "permissions": get_role_permissions(role),
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e


def require_role(allowed_roles: list[str]):
    """Decorator to require specific roles"""

    async def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user['role']} is not authorized",
            )
        return current_user

    return role_checker


def get_role_permissions(role: str) -> list[str]:
    """Get permissions for a role"""
    permissions_map = {
        "analyst": [
            "read:case:own",
            "create:observation",
            "read:observation:own",
        ],
        "lead_partner": [
            "read:case:all",
            "read:observation:all",
            "approve:observation",
            "generate:report",
        ],
        "ic_member": [
            "read:case:all",
            "read:observation:all",
            "read:conflict",
            "approve:observation",
            "generate:report",
            "export:ic_report",
            "export:lp_report",
        ],
        "admin": ["*"],
    }
    return permissions_map.get(role, [])


def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req_{uuid.uuid4().hex[:12]}"
