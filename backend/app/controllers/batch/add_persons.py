"""Add Persons Controller"""
from typing import Optional

from app.services.batch import AddPersonsService


class AddPersonsController:
    """Controller for adding persons to face recognition database."""
    
    def __init__(self, service: AddPersonsService):
        self.service = service
    
    async def add_persons(self, source_path: Optional[str] = None, move_to_backup: bool = True) -> dict:
        """Add persons from folder to database."""
        return await self.service.add_persons_from_folder(source_path, move_to_backup)
    
    async def get_known_persons(self) -> dict:
        """Get list of all known persons."""
        persons = await self.service.list_known_persons()
        return {"success": True, "persons": persons, "count": len(persons)}
