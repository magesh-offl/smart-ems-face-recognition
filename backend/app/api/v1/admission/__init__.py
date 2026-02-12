"""Admin API Router Package"""
from .routes import router
from .group_recognition import router as group_recognition_router

__all__ = ["router", "group_recognition_router"]

