"""
Dependency Injection Providers

This module provides factory functions that create instances of services and repositories.
These are used with FastAPI's Depends() for dependency injection.
"""
from functools import lru_cache
from typing import Generator

from app.repositories.recognition import RecognitionRepository
from app.repositories.batch_recognition import BatchRecognitionRepository
from app.services.recognition import RecognitionService
from app.services.batch_recognition import BatchRecognitionService


# ============================================================================
# Repository Providers
# ============================================================================

@lru_cache()
def get_recognition_repository() -> RecognitionRepository:
    """
    Provides a cached RecognitionRepository instance.
    Uses lru_cache for singleton-like behavior within the application.
    """
    return RecognitionRepository()


@lru_cache()
def get_batch_recognition_repository() -> BatchRecognitionRepository:
    """
    Provides a cached BatchRecognitionRepository instance.
    """
    return BatchRecognitionRepository()


# ============================================================================
# Service Providers
# ============================================================================

def get_recognition_service() -> RecognitionService:
    """
    Provides a RecognitionService instance with injected repository.
    """
    repository = get_recognition_repository()
    return RecognitionService(repository)


def get_batch_recognition_service() -> BatchRecognitionService:
    """
    Provides a BatchRecognitionService instance with injected repository.
    """
    repository = get_batch_recognition_repository()
    return BatchRecognitionService(repository)
