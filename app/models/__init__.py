"""Models Package - Database Document Structures

This package contains MongoDB document models that define the structure
of data stored in the database.
"""

from .base import BaseDocument
from .recognition import RecognitionLogDocument
from .batch_recognition import BatchRecognitionLogDocument
from .user import UserDocument, APIKeyDocument

__all__ = [
    "BaseDocument",
    "RecognitionLogDocument",
    "BatchRecognitionLogDocument",
    "UserDocument",
    "APIKeyDocument",
]
