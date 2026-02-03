"""Authentication API Routes - Optimized"""
from fastapi import APIRouter, Depends

from app.controllers.auth import AuthController
from app.services.auth import AuthService
from app.models import UserCreate, TokenResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ============= Dependency Injection Providers =============

def get_auth_service() -> AuthService:
    """Provides AuthService instance"""
    return AuthService()


def get_auth_controller(
    service: AuthService = Depends(get_auth_service)
) -> AuthController:
    """Provides AuthController with injected service"""
    return AuthController(service)


# ============= Auth Endpoints =============

@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Register a new user.
    
    - **username**: Username for the account (3-50 characters)
    - **password**: Password for the account (minimum 8 characters)
    """
    return controller.register(user_data.username, user_data.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserCreate,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Login with username and password.
    
    Returns JWT access token for use in subsequent requests.
    """
    return controller.login(user_data.username, user_data.password)
