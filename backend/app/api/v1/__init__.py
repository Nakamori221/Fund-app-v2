"""API v1 module"""

from fastapi import APIRouter

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.audit_logs import router as audit_logs_router
from app.api.v1.cases import router as cases_router
from app.api.v1.observations import router as observations_router
from app.api.v1.conflicts import router as conflicts_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(auth_router, tags=["認証"])
router.include_router(users_router, tags=["ユーザー管理"])
router.include_router(audit_logs_router, tags=["監査ログ"])
router.include_router(cases_router, prefix="/cases", tags=["ケース"])
router.include_router(observations_router, prefix="/cases", tags=["観察記録"])
router.include_router(conflicts_router, prefix="/cases", tags=["競合"])


__all__ = ["router"]
