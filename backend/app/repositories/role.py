"""Role Repository - CRUD for roles collection"""
from typing import List, Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import RoleDocument


class RoleRepository(BaseRepository):
    """Async repository for role management."""
    
    def __init__(self):
        super().__init__(RoleDocument.collection_name)
    
    async def create_role(self, role_data: Dict[str, Any]) -> str:
        """Create a new role."""
        return await self.create(role_data)
    
    async def get_by_role_id(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get role by semantic role_id (e.g., ROL0001)."""
        return await self.find_one({"role_id": role_id})
    
    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get role by name (e.g., 'admin')."""
        return await self.find_one({"name": name})
    
    async def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all roles."""
        return await self.find_all()
    
    async def role_exists(self, role_id: str) -> bool:
        """Check if role exists by role_id."""
        return await self.find_one({"role_id": role_id}) is not None
    
    async def seed_default_roles(self) -> List[str]:
        """Seed default system roles if they don't exist.
        
        Returns:
            List of created role_ids
        """
        created = []
        for role_data in RoleDocument.get_default_roles():
            if not await self.role_exists(role_data["role_id"]):
                doc = RoleDocument.create(**role_data)
                await self.create(doc)
                created.append(role_data["role_id"])
        return created
