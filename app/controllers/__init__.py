"""Controllers Package"""
from .auth import AuthController
from .recognition import RecognitionController
from .batch import BatchRecognitionController, AddPersonsController

__all__ = [
    "AuthController",
    "RecognitionController",
    "BatchRecognitionController",
    "AddPersonsController",
]
