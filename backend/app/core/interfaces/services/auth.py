"""Auth Service Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IAuthService(ABC):
    """Interface for authentication services"""
    
    @abstractmethod
    def register(self, username: str, password: str) -> str:
        """Register a new user, returns user ID"""
        pass
    
    @abstractmethod
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Login and return token data"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data"""
        pass
