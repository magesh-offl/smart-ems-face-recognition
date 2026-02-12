"""Schemas Package - API Request/Response Validation

This package contains Pydantic models for API validation, organized by:
- requests/: Input validation schemas
- responses/: Output formatting schemas  
- filters/: Query filter schemas
"""

# Base schemas
from .base import (
    TimestampMixin,
    PaginationParams,
    SuccessResponse,
    ErrorResponse
)

# Request schemas
from .requests import (
    RecognitionLogCreate,
    RecognitionLogUpdate,
    BatchRecognitionRequest,
    AddPersonsRequest,
    UserCreate,
    UserUpdate,
    LoginRequest,
    RegisterRequest,
    ForgotPasswordRequest,
    APIKeyCreate,
)

# Response schemas
from .responses import (
    RecognitionLogResponse,
    FaceLocation,
    BatchRecognitionResult,
    BatchRecognitionResponse,
    AddPersonsResponse,
    UserResponse,
    TokenResponse,
    APIKeyResponse,
)

# Filter schemas
from .filters import (
    RecognitionLogFilter,
    BatchRecognitionFilter,
)

__all__ = [
    # Base
    "TimestampMixin",
    "PaginationParams",
    "SuccessResponse",
    "ErrorResponse",
    # Requests
    "RecognitionLogCreate",
    "RecognitionLogUpdate",
    "BatchRecognitionRequest",
    "AddPersonsRequest",
    "UserCreate",
    "UserUpdate",
    "LoginRequest",
    "RegisterRequest",
    "ForgotPasswordRequest",
    "APIKeyCreate",
    # Responses
    "RecognitionLogResponse",
    "FaceLocation",
    "BatchRecognitionResult",
    "BatchRecognitionResponse",
    "AddPersonsResponse",
    "UserResponse",
    "TokenResponse",
    "APIKeyResponse",
    # Filters
    "RecognitionLogFilter",
    "BatchRecognitionFilter",
]
