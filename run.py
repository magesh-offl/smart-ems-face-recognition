#!/usr/bin/env python3
"""Application Entry Point"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",  # Import string for uvicorn to reload properly
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=(settings.API_ENV == "development"),
        log_level=settings.LOG_LEVEL.lower()
    )
