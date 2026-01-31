"""
ragebAIt - AI Sports Miscommentary Generator

FastAPI backend for generating comedic AI commentary on sports videos.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import generate_router, meme_router
from backend.models.schemas import HealthResponse


# Create FastAPI app
app = FastAPI(
    title="ragebAIt API",
    description="AI Sports Miscommentary Generator - Turn any sports clip into comedy gold",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router)
app.include_router(meme_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "name": "ragebAIt",
        "tagline": "AI Sports Miscommentary Generator",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns status of all services.
    """
    from backend.services.tts_client import tts_client
    from backend.services.storage_client import storage_client
    
    services = {
        "gemini": bool(settings.GEMINI_API_KEY),
        "tts_fal": tts_client.is_available(),  # fal.ai TTS
        "storage": storage_client.is_available(),
    }
    
    return HealthResponse(
        status="ok" if all(services.values()) else "degraded",
        version="1.0.0",
        services=services
    )


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 50)
    print("🎬 ragebAIt API Starting...")
    print("=" * 50)
    
    # Validate settings
    errors = settings.validate()
    if errors:
        print("⚠️  Configuration warnings:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuration valid")
    
    # Check services
    from backend.services.tts_client import tts_client
    from backend.services.storage_client import storage_client
    
    print(f"   Gemini API: {'✅' if settings.GEMINI_API_KEY else '❌'}")
    print(f"   fal.ai TTS: {'✅' if tts_client.is_available() else '❌'}")
    print(f"   Storage: {'✅' if storage_client.is_available() else '❌'}")
    
    print("=" * 50)
    print("🚀 Ready to generate sports miscommentary!")
    print("   Docs: http://localhost:8000/docs")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 ragebAIt API shutting down...")


# Entry point for running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
