"""Services Package"""
from .auth import AuthService
from .recognition import RecognitionService
from .batch import BatchRecognitionService, AddPersonsService

__all__ = [
    "AuthService",
    "RecognitionService",
    "BatchRecognitionService",
    "AddPersonsService",
]
