#!/usr/bin/env python3
"""Inference Service Entry Point"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    # FOR PRODUCTION:
    #    Set INFERENCE_ENV=production in your .env file

    uvicorn.run(
        "app.main:app",
        host=settings.INFERENCE_HOST,
        port=settings.INFERENCE_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=(settings.ENV == "development"),
        workers=settings.WORKERS,
    )
