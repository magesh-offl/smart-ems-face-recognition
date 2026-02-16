"""Inference Service — FastAPI Application Entry Point

Serves ML inference endpoints for face detection, recognition,
embedding extraction, and feature store management.
"""
import logging
from fastapi import FastAPI
from app.config import get_settings
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Smart EMS — Inference Service",
    description="ML inference microservice for face detection and recognition",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": "inference",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.on_event("startup")
async def startup_event():
    """Load ML models on startup so the first request isn't slow."""
    logger.info("Inference service starting up…")
    logger.info(f"Detection model : {settings.DETECTION_MODEL}")
    logger.info(f"Recognition model: {settings.RECOGNITION_MODEL}")

    # Eagerly load models (blocking, but only once at startup)
    try:
        from app.services.detector import get_detector, get_detector_type
        get_detector()
        logger.info(f"Detector loaded : {get_detector_type()}")
    except Exception as e:
        logger.error(f"Failed to load detector: {e}")

    try:
        from app.services.recognizer import get_recognizer, get_recognizer_type
        get_recognizer()
        logger.info(f"Recognizer loaded: {get_recognizer_type()}")
    except Exception as e:
        logger.error(f"Failed to load recognizer: {e}")

    try:
        from app.services.feature_store import get_features
        names, embs = get_features()
        if names is not None:
            logger.info(f"Features loaded  : {len(names)} embeddings, "
                        f"{len(set(names.tolist()))} persons")
        else:
            logger.warning("No pre-computed features found (gallery empty)")
    except Exception as e:
        logger.error(f"Failed to load features: {e}")

    logger.info("Inference service ready ✓")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    logger.info("Inference service shutting down")
