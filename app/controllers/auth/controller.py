"""Auth Controller"""
from app.services.auth import AuthService
from app.schemas import TokenResponse


class AuthController:
    """Controller for authentication operations."""
    
    def __init__(self, service: AuthService):
        self.service = service
    
    def register(self, username: str, password: str) -> dict:
        """Register a new user."""
        user_id = self.service.register_user(username, password)
        return {"success": True, "user_id": user_id, "message": f"User {username} registered"}
    
    def login(self, username: str, password: str) -> TokenResponse:
        """Login and get access token."""
        token = self.service.login_user(username, password)
        return TokenResponse(
            access_token=token,
            expires_in=self.service.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
