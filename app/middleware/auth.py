"""
Authentication Middleware

Provides authentication utilities for API endpoints using Dependency Injection.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer

from app.services.auth import AuthService
from app.core.dependencies.auth import get_auth_service
from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
security = HTTPBearer()


# ============================================================================
# JWT Token Authentication (DI-compliant)
# ============================================================================

async def verify_token(
    credentials=Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """
    Verify JWT token from Authorization header.
    
    Uses dependency injection for AuthService.
    
    Args:
        credentials: Bearer token from Authorization header
        auth_service: Injected AuthService instance
        
    Returns:
        Username from the verified token
        
    Raises:
        HTTPException 401: If token is invalid or expired
    """
    token = credentials.credentials
    username = auth_service.verify_token(token)
    
    if not username:
        logger.warning(f"Invalid token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return username


# ============================================================================
# API Key Authentication
# ============================================================================

def _verify_api_key(api_key: str) -> bool:
    """
    Internal helper to verify API key against settings.
    
    Args:
        api_key: API key to verify
        
    Returns:
        True if valid, False otherwise
    """
    settings = get_settings()
    return api_key == settings.API_KEY


async def require_api_key(
    x_api_key: str = Header(None, alias="X-API-Key")
) -> str:
    """
    FastAPI dependency for API key authentication.
    
    Use with Depends(require_api_key) in route parameters.
    Automatically extracts X-API-Key from header and validates it.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException 401: If API key is missing
        HTTPException 403: If API key is invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required in X-API-Key header"
        )
    
    if not _verify_api_key(x_api_key):
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return x_api_key
