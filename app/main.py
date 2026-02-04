"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.auth import router as auth_router
from app.api.v1.recognition import router as recognition_router
from app.middleware import register_exception_handlers
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Face Recognition Backend",
    description="API for managing face recognition data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Register global exception handlers
register_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(recognition_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Face Recognition Backend API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.API_ENV
    }


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("Application started")
    logger.info(f"Environment: {settings.API_ENV}")
    logger.info(f"MongoDB: {settings.MONGO_DB_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Application shutdown")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=(settings.API_ENV == "development")
    )
