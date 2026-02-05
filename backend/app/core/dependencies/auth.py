"""Auth Dependency Providers"""
from functools import lru_cache

from app.repositories.user import UserRepository
from app.services.auth import AuthService


@lru_cache()
def get_user_repository() -> UserRepository:
    """Provides a cached UserRepository instance."""
    return UserRepository()


def get_auth_service() -> AuthService:
    """Provides an AuthService with injected repository."""
    repository = get_user_repository()
    return AuthService(repository)
