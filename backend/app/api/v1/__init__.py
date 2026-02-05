"""API v1 Package"""
from .auth import router as auth_router
from .recognition import router as recognition_router

__all__ = ["auth_router", "recognition_router"]
