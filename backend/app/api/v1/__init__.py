"""API v1 module"""

from fastapi import APIRouter

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.cases import router as cases_router
from app.api.v1.observations import router as observations_router
from app.api.v1.conflicts import router as conflicts_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(cases_router, prefix="/cases", tags=["Cases"])
router.include_router(observations_router, prefix="/cases", tags=["Observations"])
router.include_router(conflicts_router, prefix="/cases", tags=["Conflicts"])

__all__ = ["router"]
