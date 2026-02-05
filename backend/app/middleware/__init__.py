"""
Middleware Package

This package contains cross-cutting concerns that apply across multiple endpoints:
- Authentication (auth.py)
- Error handling (error_handling.py)
"""

from .auth import verify_token, require_api_key
from .error_handling import register_exception_handlers, ErrorResponse

__all__ = [
    # Authentication
    "verify_token",
    "require_api_key",
    # Error handling
    "register_exception_handlers",
    "ErrorResponse",
]
