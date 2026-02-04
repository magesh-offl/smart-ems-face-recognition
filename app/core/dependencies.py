"""
Dependency Injection Providers (Backwards Compatibility)

This module re-exports providers from the dependencies package
for backwards compatibility with existing imports.

For new code, import directly from app.core.dependencies package:
    from app.core.dependencies import get_recognition_service
"""

from app.core.dependencies import (
    get_recognition_repository,
    get_recognition_service,
    get_batch_recognition_repository,
    get_batch_recognition_service,
    get_user_repository,
    get_auth_service,
)

__all__ = [
    "get_recognition_repository",
    "get_recognition_service",
    "get_batch_recognition_repository",
    "get_batch_recognition_service",
    "get_user_repository",
    "get_auth_service",
]
