"""API v1 module"""

from fastapi import APIRouter

# Import routers
from app.api.v1.cases import router as cases_router
from app.api.v1.auth import router as auth_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(cases_router, prefix="/cases", tags=["Cases"])

__all__ = ["router"]
