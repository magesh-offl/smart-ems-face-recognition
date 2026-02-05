"""Batch Recognition Dependency Providers"""
from functools import lru_cache

from app.repositories.batch_recognition import BatchRecognitionRepository
from app.services.batch import BatchRecognitionService


@lru_cache()
def get_batch_recognition_repository() -> BatchRecognitionRepository:
    """Provides a cached BatchRecognitionRepository instance."""
    return BatchRecognitionRepository()


def get_batch_recognition_service() -> BatchRecognitionService:
    """Provides a BatchRecognitionService with injected repository."""
    repository = get_batch_recognition_repository()
    return BatchRecognitionService(repository)
