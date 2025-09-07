"""
Integraite Backend API
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.init_db import init_database
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        # await init_database()
        print(f"🚀 Integraite API starting up in {settings.ENVIRONMENT} mode")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Continue startup even if database init fails (for development)
        if settings.ENVIRONMENT == "production":
            raise
    
    yield
    
    # Shutdown
    print("🔄 Integraite API shutting down")


# Create FastAPI application
app = FastAPI(
    title="Integraite API",
    description="Autonomous Self-Healing Ops Platform API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["integraite.com", "*.integraite.com"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Integraite API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "Contact support for API documentation"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": "2024-01-01T00:00:00Z"  # This would be actual timestamp
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
