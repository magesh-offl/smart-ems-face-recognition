"""Authentication API Routes"""
from fastapi import APIRouter, Depends

from app.controllers.auth import AuthController
from app.core.dependencies import get_auth_service
from app.schemas import UserCreate, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_auth_controller(service=Depends(get_auth_service)) -> AuthController:
    return AuthController(service)


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    controller: AuthController = Depends(get_auth_controller)
):
    """Register a new user."""
    return controller.register(user_data.username, user_data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserCreate,
    controller: AuthController = Depends(get_auth_controller)
):
    """Login with username and password. Returns JWT access token."""
    return controller.login(user_data.username, user_data.password)
