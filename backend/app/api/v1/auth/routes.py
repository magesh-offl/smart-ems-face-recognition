"""Authentication API Routes - Async with RBAC Support"""
from fastapi import APIRouter, Depends

from app.services.auth import AuthService
from app.core.dependencies import get_auth_service
from app.schemas import (
    LoginRequest, 
    RegisterRequest, 
    ForgotPasswordRequest, 
    TokenResponse
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
async def register(
    user_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user with role assignment.
    
    Default role is student (ROL0004).
    Requires: username, password, email
    Optional: role_id, first_name, last_name
    """
    return await auth_service.register(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        role_id=user_data.role_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with username and password. 
    
    Returns JWT access token with role claims.
    """
    return await auth_service.login(
        username=user_data.username,
        password=user_data.password
    )


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset.
    
    Creates a reset request for admin review (NOT email-based).
    Admin will see the request in their dashboard and communicate
    the new password to the user.
    """
    return await auth_service.forgot_password(username=request.username)
