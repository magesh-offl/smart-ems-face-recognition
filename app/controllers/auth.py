"""Auth Controller - Orchestrates authentication operations"""
from typing import Dict, Any

from app.services.auth import AuthService
from app.models import TokenResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthController:
    """Controller for authentication operations"""
    
    def __init__(self, service: AuthService = None):
        self.service = service or AuthService()
    
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username for the account
            password: Password for the account
        
        Returns:
            Dict with success status and user_id
        """
        user_id = self.service.register_user(username, password)
        logger.info(f"User registered: {username}")
        
        return {
            "success": True,
            "user_id": user_id,
            "message": f"User {username} registered successfully"
        }
    
    def login(self, username: str, password: str) -> TokenResponse:
        """
        Login and get access token.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            TokenResponse with access token
        """
        token = self.service.login_user(username, password)
        settings = self.service.settings
        
        logger.info(f"User logged in: {username}")
        
        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
