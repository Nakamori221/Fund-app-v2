"""FastAPI application factory and configuration"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.config import get_settings
from app.core.errors import APIException
from app.api.v1 import router as v1_router


# Application lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    settings = get_settings()
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔐 Debug: {settings.DEBUG}")

    yield

    # Shutdown
    print(f"🛑 Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Request ID middleware
    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next):
        """Add X-Request-ID to all requests and responses"""
        from app.core.security import generate_request_id

        request_id = request.headers.get("X-Request-ID", generate_request_id())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

    # Error handlers
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        settings = get_settings()

        # Log the exception
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={"request_id": getattr(request.state, "request_id", None)},
        )

        # Return error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"exception": str(exc)} if settings.DEBUG else {},
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # OpenAPI customization
    def custom_openapi():
        """Customize OpenAPI schema"""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.API_TITLE,
            version=settings.APP_VERSION,
            description=settings.API_DESCRIPTION,
            routes=app.routes,
        )

        # Add custom server information
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "Development server",
            },
            {
                "url": "http://api.example.com",
                "description": "Production server",
            },
        ]

        # Add security scheme for Bearer tokens
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT access token",
            }
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    # Include API v1 router
    app.include_router(v1_router)

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
