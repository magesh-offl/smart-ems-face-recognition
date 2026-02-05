"""Async Auth Controller"""
from app.services.auth.service import AuthService
from app.schemas import UserCreate


class AuthController:
    """Async controller for authentication."""
    
    def __init__(self, service: AuthService):
        self.service = service
    
    async def register(self, request: UserCreate) -> dict:
        """Register new user."""
        return await self.service.register(request.username, request.password)
    
    async def login(self, request: UserCreate) -> dict:
        """Login user."""
        return await self.service.login(request.username, request.password)
