"""Dependency Providers Package

This package provides factory functions for dependency injection.
Each domain has its own module for better organization and scalability.
"""

# Recognition domain
from .recognition import (
    get_recognition_repository,
    get_recognition_service
)

# Batch recognition domain
from .batch import (
    get_batch_recognition_repository,
    get_batch_recognition_service
)

# Auth domain
from .auth import (
    get_user_repository,
    get_auth_service
)

__all__ = [
    # Recognition
    "get_recognition_repository",
    "get_recognition_service",
    # Batch
    "get_batch_recognition_repository",
    "get_batch_recognition_service",
    # Auth
    "get_user_repository",
    "get_auth_service",
]
