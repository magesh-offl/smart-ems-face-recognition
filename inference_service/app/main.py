"""Inference Service — FastAPI Application Entry Point

Serves ML inference endpoints for face detection, recognition,
embedding extraction, and feature store management.

Multi-worker support:
    On startup each worker connects to Redis and spawns a background
    pub/sub listener.  When any worker trains new persons or reloads
    features, a notification is published so every peer refreshes its
    local cache automatically.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Background task handle for pub/sub listener
_pubsub_task: asyncio.Task | None = None


# =====================================================================
# Pub/Sub listener (runs as a background asyncio task per worker)
# =====================================================================

async def _feature_reload_listener() -> None:
    """Subscribe to Redis feature_reload channel.

    When a peer worker publishes a reload event, refresh the local
    feature cache from Redis.
    """
    from app.services.redis_client import get_redis, is_redis_available

    if not is_redis_available():
        return

    redis = get_redis()
    channel = settings.REDIS_CHANNEL

    while True:
        try:
            pubsub = redis.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Pub/Sub listener subscribed to '{channel}'")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    logger.info("Received feature_reload event from peer worker")
                    from app.services.feature_store import refresh_from_redis
                    await refresh_from_redis()

        except asyncio.CancelledError:
            logger.info("Pub/Sub listener cancelled")
            break
        except Exception as e:
            logger.warning(f"Pub/Sub listener error: {e} — reconnecting in 3s")
            await asyncio.sleep(3)


# =====================================================================
# Lifespan (startup / shutdown)
# =====================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs once per worker process."""
    global _pubsub_task

    logger.info("Inference service starting up…")
    logger.info(f"Detection model : {settings.DETECTION_MODEL}")
    logger.info(f"Recognition model: {settings.RECOGNITION_MODEL}")

    # ── 1. Connect to Redis ──────────────────────────────────────────
    from app.services.redis_client import init_redis, close_redis, is_redis_available

    redis_ok = await init_redis()
    if redis_ok:
        logger.info("Redis connected — multi-worker sync enabled")
    else:
        logger.warning("Redis unavailable — running in single-worker mode")

    # ── 2. Load ML models (blocking, but only once at startup) ───────
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

    # ── 3. Load feature gallery ──────────────────────────────────────
    try:
        if redis_ok:
            from app.services.feature_store import reload_features_async
            num_persons, num_embs = await reload_features_async()
            if num_embs > 0:
                logger.info(f"Features loaded (Redis-synced): {num_embs} embeddings, {num_persons} persons")
            else:
                logger.warning("No pre-computed features found (gallery empty)")
        else:
            from app.services.feature_store import get_features
            names, embs = get_features()
            if names is not None:
                logger.info(f"Features loaded  : {len(names)} embeddings, "
                            f"{len(set(names.tolist()))} persons")
            else:
                logger.warning("No pre-computed features found (gallery empty)")
    except Exception as e:
        logger.error(f"Failed to load features: {e}")

    # ── 4. Start pub/sub listener ────────────────────────────────────
    if redis_ok:
        _pubsub_task = asyncio.create_task(_feature_reload_listener())

    logger.info("Inference service ready ✓")

    # ── yield (app runs here) ────────────────────────────────────────
    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    logger.info("Inference service shutting down…")

    if _pubsub_task is not None:
        _pubsub_task.cancel()
        try:
            await _pubsub_task
        except asyncio.CancelledError:
            pass

    await close_redis()
    logger.info("Inference service stopped")


# =====================================================================
# FastAPI app
# =====================================================================

app = FastAPI(
    title="Smart EMS — Inference Service",
    description="ML inference microservice for face detection and recognition",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
