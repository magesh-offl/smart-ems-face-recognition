"""Inference Service Configuration

ML model selection, paths, thresholds — single source of truth.
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


# =============================================================================
# PROJECT PATHS (derived from file location)
# =============================================================================
# inference_service/app/config.py → PROJECT_ROOT = inference_service/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class InferenceSettings(BaseSettings):
    """Inference service settings loaded from environment variables."""

    # Server
    INFERENCE_HOST: str = "0.0.0.0"
    INFERENCE_PORT: int = 8010
    WORKERS: int = 2  # Control multiprocessing (default 1)
    
    # Environment: "development" or "production"
    # In production: Set this to "production" to disable auto-reload and enable optimizations
    ENV: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:8000"]

    # Detection model: "yolov12" or "scrfd"
    DETECTION_MODEL: str = "yolov12"

    # Recognition model: "adaface" or "arcface"
    RECOGNITION_MODEL: str = "adaface"

    # Preprocessing
    ENABLE_PREPROCESSING: bool = True
    MIN_IMAGE_WIDTH: int = 1920
    ENABLE_UPSCALING: bool = True
    ENABLE_CLAHE: bool = False  # Disabled — causes false positives

    # Recognition
    CONFIDENCE_THRESHOLD: float = 0.4

    # Paths (relative to PROJECT_ROOT)
    DATASETS_PATH: str = ""  # Will be resolved to absolute path
    FEATURE_PATH: str = ""   # Will be resolved to absolute path

    # Redis (multi-worker feature sync)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_FEATURE_KEY: str = "inference:features"           # gallery data key
    REDIS_FEATURE_VERSION_KEY: str = "inference:features:version"  # version counter
    REDIS_CHANNEL: str = "inference:feature_reload"         # pub/sub channel
    REDIS_LOCK_KEY: str = "inference:train_lock"            # distributed lock
    REDIS_LOCK_TIMEOUT: int = 300                           # max lock hold (seconds)

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> InferenceSettings:
    """Get cached settings instance."""
    settings = InferenceSettings()

    # Resolve default paths relative to the backend datasets location
    # The datasets live in the backend directory (backend manages file uploads)
    backend_root = os.path.join(os.path.dirname(PROJECT_ROOT), "backend")

    if not settings.DATASETS_PATH:
        settings.DATASETS_PATH = os.path.join(backend_root, "datasets")

    if not settings.FEATURE_PATH:
        settings.FEATURE_PATH = os.path.join(
            backend_root, "datasets", "face_features"
        )

    return settings
