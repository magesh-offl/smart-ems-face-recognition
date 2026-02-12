"""Models Package - Database Document Structures

This package contains MongoDB document models that define the structure
of data stored in the database.
"""

from .base import BaseDocument
from .recognition import RecognitionLogDocument
from .batch_recognition import BatchRecognitionLogDocument
from .user import UserDocument, APIKeyDocument
from .id_counter import IDCounterDocument
from .role import RoleDocument
from .course import CourseDocument
from .student import StudentDocument
from .admission import AdmissionDocument

from .student_log import StudentLogDocument
from .password_reset import PasswordResetDocument

__all__ = [
    "BaseDocument",
    "RecognitionLogDocument",
    "BatchRecognitionLogDocument",
    "UserDocument",
    "APIKeyDocument",
    "IDCounterDocument",
    "RoleDocument",
    "CourseDocument",
    "StudentDocument",
    "AdmissionDocument",

    "StudentLogDocument",
    "PasswordResetDocument",
]

