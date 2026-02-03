"""Authentication utilities for API endpoints"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer
from starlette.requests import Request
from app.services.auth import AuthService
from app.config import get_settings

security = HTTPBearer()


def verify_token(credentials = Depends(security)) -> str:
    """Verify JWT token from Authorization header"""
    auth_service = AuthService()
    token = credentials.credentials
    
    username = auth_service.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return username


def verify_api_key(api_key: str) -> bool:
    """Verify API key"""
    settings = get_settings()
    return api_key == settings.API_KEY


async def verify_api_key_header(request_api_key: str = None) -> bool:
    """Verify API key from header (legacy - use require_api_key instead)"""
    if not request_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    if not verify_api_key(request_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return True


async def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """
    FastAPI dependency for API key authentication.
    
    Use with Depends(require_api_key) in route parameters.
    Automatically extracts X-API-Key from header and validates it.
    
    Raises:
        HTTPException 401: If API key is missing
        HTTPException 403: If API key is invalid
    
    Returns:
        The validated API key
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required in X-API-Key header"
        )
    
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return x_api_key

