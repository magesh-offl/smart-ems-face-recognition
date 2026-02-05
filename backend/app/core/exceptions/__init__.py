"""
Core Exceptions Package

Domain exceptions represent business logic errors.
HTTP exceptions are in utils/exceptions.py
Exception handlers are in middleware/error_handling.py
"""

from .domain import (
    # Base
    DomainException,
    # Recognition
    FaceNotDetectedException,
    FaceNotRecognizedException,
    MultipleFacesException,
    # Model
    ModelNotLoadedException,
    ModelNotTrainedException,
    FeatureExtractionException,
    # Data
    InvalidImageException,
    PersonAlreadyExistsException,
    PersonNotFoundException,
)

__all__ = [
    "DomainException",
    "FaceNotDetectedException",
    "FaceNotRecognizedException",
    "MultipleFacesException",
    "ModelNotLoadedException",
    "ModelNotTrainedException",
    "FeatureExtractionException",
    "InvalidImageException",
    "PersonAlreadyExistsException",
    "PersonNotFoundException",
]
