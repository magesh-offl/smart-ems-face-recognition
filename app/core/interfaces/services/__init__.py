"""Service Interfaces Package"""
from .recognition import IRecognitionService
from .batch import IBatchRecognitionService
from .auth import IAuthService

__all__ = [
    "IRecognitionService",
    "IBatchRecognitionService",
    "IAuthService",
]
