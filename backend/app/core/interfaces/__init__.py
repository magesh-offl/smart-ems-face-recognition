"""Interfaces Package

This package contains abstract base classes that define contracts
for repositories, services, and controllers.
"""

# Repository interface
from .repository import IRepository

# Service interfaces
from .services import (
    IRecognitionService,
    IBatchRecognitionService,
    IAuthService
)

# For backwards compatibility with existing imports
from .service import IService

__all__ = [
    # Repository
    "IRepository",
    # Services
    "IService",
    "IRecognitionService",
    "IBatchRecognitionService",
    "IAuthService",
]
