"""Batch Recognition Dependency Providers"""
from functools import lru_cache

from app.repositories.batch_recognition import BatchRecognitionRepository
from app.services.batch import BatchRecognitionService, AddPersonsService
from app.core.inference_client import InferenceClient


@lru_cache()
def get_batch_recognition_repository() -> BatchRecognitionRepository:
    """Provides a cached BatchRecognitionRepository instance."""
    return BatchRecognitionRepository()


@lru_cache()
def get_inference_client() -> InferenceClient:
    """Provides a cached InferenceClient singleton."""
    return InferenceClient()


def get_batch_recognition_service() -> BatchRecognitionService:
    """Provides a BatchRecognitionService with injected dependencies."""
    repository = get_batch_recognition_repository()
    inference = get_inference_client()
    return BatchRecognitionService(repository=repository, inference_client=inference)


def get_add_persons_service() -> AddPersonsService:
    """Provides an AddPersonsService with injected InferenceClient."""
    inference = get_inference_client()
    return AddPersonsService(inference_client=inference)
