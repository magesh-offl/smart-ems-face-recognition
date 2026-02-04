"""
Domain Exceptions

Business logic exceptions that represent domain-specific error conditions.
These are NOT HTTP exceptions - they represent errors in business logic.
They should be caught and converted to HTTP responses by the middleware layer.
"""


class DomainException(Exception):
    """Base class for all domain exceptions"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ============================================================================
# Recognition Domain Exceptions
# ============================================================================

class FaceNotDetectedException(DomainException):
    """Raised when no face is detected in an image"""
    def __init__(self, image_path: str = None):
        message = "No face detected in the image"
        details = {"image_path": image_path} if image_path else {}
        super().__init__(message, details)


class FaceNotRecognizedException(DomainException):
    """Raised when a face is detected but cannot be recognized"""
    def __init__(self, confidence_score: float = None):
        message = "Face detected but could not be recognized"
        details = {"confidence_score": confidence_score} if confidence_score else {}
        super().__init__(message, details)


class MultipleFacesException(DomainException):
    """Raised when multiple faces are detected but only one is expected"""
    def __init__(self, face_count: int):
        message = f"Expected single face, found {face_count} faces"
        super().__init__(message, {"face_count": face_count})


# ============================================================================
# Model Domain Exceptions
# ============================================================================

class ModelNotLoadedException(DomainException):
    """Raised when ML model is not loaded"""
    def __init__(self, model_name: str):
        message = f"Model '{model_name}' is not loaded"
        super().__init__(message, {"model_name": model_name})


class ModelNotTrainedException(DomainException):
    """Raised when model has no trained data"""
    def __init__(self):
        message = "Model has no trained data. Please add persons first."
        super().__init__(message)


class FeatureExtractionException(DomainException):
    """Raised when feature extraction fails"""
    def __init__(self, reason: str = None):
        message = "Failed to extract features from image"
        details = {"reason": reason} if reason else {}
        super().__init__(message, details)


# ============================================================================
# Data Domain Exceptions
# ============================================================================

class InvalidImageException(DomainException):
    """Raised when image is invalid or corrupted"""
    def __init__(self, image_path: str, reason: str = None):
        message = f"Invalid image: {image_path}"
        details = {"image_path": image_path}
        if reason:
            details["reason"] = reason
        super().__init__(message, details)


class PersonAlreadyExistsException(DomainException):
    """Raised when trying to add a person that already exists"""
    def __init__(self, person_name: str):
        message = f"Person '{person_name}' already exists in the database"
        super().__init__(message, {"person_name": person_name})


class PersonNotFoundException(DomainException):
    """Raised when a person is not found in the database"""
    def __init__(self, person_name: str):
        message = f"Person '{person_name}' not found in the database"
        super().__init__(message, {"person_name": person_name})
