from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from src.core.config import settings
from src.api.routes import query, health
from src.monitoring.logger import setup_logging
from src.core.exceptions import PlainAPIException

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")
    
    # Create data directories
    from src.core.config import create_directories
    create_directories()
    
    yield
    
    # Shutdown
    logger.info("Shutting down PlainAPI")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered API Simplification System",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handler
    @app.exception_handler(PlainAPIException)
    async def plainapi_exception_handler(request: Request, exc: PlainAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.message,
                "detail": exc.detail
            }
        )
    
    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(query.router, prefix="/api", tags=["query"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "environment": settings.app_env,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
