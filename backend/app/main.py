"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.auth import router as auth_router
from app.api.v1.recognition import router as recognition_router
from app.api.v1.admission import router as admission_router
from app.api.v1.admission import group_recognition_router
from app.middleware import register_exception_handlers
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Smart EMS - Face Recognition Backend",
    description="API for Smart Education Management System with Face Recognition",
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
app.include_router(admission_router)
app.include_router(group_recognition_router)


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
    """Startup event - initialize database and create super admin"""
    logger.info("Application started")
    logger.info(f"Environment: {settings.API_ENV}")
    logger.info(f"MongoDB: {settings.MONGO_DB_URL}")
    
    # Create super admin if not exists (and seed default roles)
    try:
        from app.api.deps import get_auth_service
        auth_service = get_auth_service()
        result = await auth_service.create_super_admin_if_not_exists()
        if result:
            logger.info(f"Super admin created: {result['username']}")
    except Exception as e:
        logger.error(f"Failed to create super admin: {e}")
    
    # Seed default courses if not exists
    try:
        from app.core.seed import get_seeder_service
        seeder = get_seeder_service()
        results = await seeder.seed_all()
        
        for name, count in results.items():
            if count > 0:
                logger.info(f"Seeded {count} {name}")
            elif count == 0:
                logger.info(f"All {name} already seeded")
            else:
                logger.warning(f"Failed to seed {name}")
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")


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
