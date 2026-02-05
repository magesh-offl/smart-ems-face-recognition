"""Recognition Dependency Providers"""
from functools import lru_cache

from app.repositories.recognition import RecognitionRepository
from app.services.recognition import RecognitionService


@lru_cache()
def get_recognition_repository() -> RecognitionRepository:
    """Provides a cached RecognitionRepository instance."""
    return RecognitionRepository()


def get_recognition_service() -> RecognitionService:
    """Provides a RecognitionService with injected repository."""
    repository = get_recognition_repository()
    return RecognitionService(repository)
