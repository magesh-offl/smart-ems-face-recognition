"""Auth Dependency Providers"""
from functools import lru_cache

from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.password_reset import PasswordResetRepository
from app.services.auth import AuthService
from app.services.id_generator import IDGeneratorService, IDCounterRepository


@lru_cache()
def get_user_repository() -> UserRepository:
    """Provides a cached UserRepository instance."""
    return UserRepository()


@lru_cache()
def get_role_repository() -> RoleRepository:
    """Provides a cached RoleRepository instance."""
    return RoleRepository()


@lru_cache()
def get_password_reset_repository() -> PasswordResetRepository:
    """Provides a cached PasswordResetRepository instance."""
    return PasswordResetRepository()


def get_id_generator() -> IDGeneratorService:
    """Provides an IDGeneratorService instance."""
    counter_repo = IDCounterRepository()
    return IDGeneratorService(counter_repo)


def get_auth_service() -> AuthService:
    """Provides an AuthService with all injected dependencies."""
    return AuthService(
        user_repository=get_user_repository(),
        role_repository=get_role_repository(),
        password_reset_repository=get_password_reset_repository(),
        id_generator=get_id_generator()
    )
