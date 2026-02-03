"""
Global Exception Handlers

This module provides centralized exception handling for the FastAPI application.
Implements industry-standard error response format with request tracking.
"""
import uuid
import traceback
from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.utils.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    BadRequestException,
    InternalServerException
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def create(
        status_code: int,
        error_type: str,
        message: str,
        request_id: str,
        details: Optional[Any] = None,
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            status_code: HTTP status code
            error_type: Type of error (e.g., "ValidationError", "NotFound")
            message: Human-readable error message
            request_id: Unique request identifier for tracking
            details: Optional additional error details
            path: Request path that caused the error
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        if path:
            response["error"]["path"] = path
            
        if details:
            response["error"]["details"] = details
            
        return response


def get_request_id(request: Request) -> str:
    """Get or generate a request ID for tracking"""
    # Check if request ID was passed in header
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    return request_id


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        request_id = get_request_id(request)
        
        # Format validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error | request_id={request_id} | "
            f"path={request.url.path} | errors={errors}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse.create(
                status_code=422,
                error_type="ValidationError",
                message="Request validation failed",
                request_id=request_id,
                path=request.url.path,
                details=errors
            )
        )
    
    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(
        request: Request, 
        exc: AuthenticationException
    ) -> JSONResponse:
        """Handle authentication failures"""
        request_id = get_request_id(request)
        
        logger.warning(
            f"Authentication failed | request_id={request_id} | "
            f"path={request.url.path} | detail={exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(
                status_code=exc.status_code,
                error_type="AuthenticationError",
                message=exc.detail,
                request_id=request_id,
                path=request.url.path
            ),
            headers=exc.headers
        )
    
    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(
        request: Request, 
        exc: AuthorizationException
    ) -> JSONResponse:
        """Handle authorization failures"""
        request_id = get_request_id(request)
        
        logger.warning(
            f"Authorization failed | request_id={request_id} | "
            f"path={request.url.path} | detail={exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(
                status_code=exc.status_code,
                error_type="AuthorizationError",
                message=exc.detail,
                request_id=request_id,
                path=request.url.path
            )
        )
    
    @app.exception_handler(ResourceNotFoundException)
    async def not_found_exception_handler(
        request: Request, 
        exc: ResourceNotFoundException
    ) -> JSONResponse:
        """Handle resource not found errors"""
        request_id = get_request_id(request)
        
        logger.info(
            f"Resource not found | request_id={request_id} | "
            f"path={request.url.path} | detail={exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(
                status_code=exc.status_code,
                error_type="NotFoundError",
                message=exc.detail,
                request_id=request_id,
                path=request.url.path
            )
        )
    
    @app.exception_handler(BadRequestException)
    async def bad_request_exception_handler(
        request: Request, 
        exc: BadRequestException
    ) -> JSONResponse:
        """Handle bad request errors"""
        request_id = get_request_id(request)
        
        logger.warning(
            f"Bad request | request_id={request_id} | "
            f"path={request.url.path} | detail={exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(
                status_code=exc.status_code,
                error_type="BadRequestError",
                message=exc.detail,
                request_id=request_id,
                path=request.url.path
            )
        )
    
    @app.exception_handler(InternalServerException)
    async def internal_server_exception_handler(
        request: Request, 
        exc: InternalServerException
    ) -> JSONResponse:
        """Handle internal server errors"""
        request_id = get_request_id(request)
        
        logger.error(
            f"Internal server error | request_id={request_id} | "
            f"path={request.url.path} | detail={exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(
                status_code=exc.status_code,
                error_type="InternalServerError",
                message=exc.detail,
                request_id=request_id,
                path=request.url.path
            )
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for unhandled exceptions.
        Logs full traceback and returns a safe error message.
        """
        request_id = get_request_id(request)
        
        # Log full traceback for debugging
        logger.error(
            f"Unhandled exception | request_id={request_id} | "
            f"path={request.url.path} | exception={type(exc).__name__}: {str(exc)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        
        # Don't expose internal details to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.create(
                status_code=500,
                error_type="InternalServerError",
                message="An unexpected error occurred. Please try again later.",
                request_id=request_id,
                path=request.url.path
            )
        )
