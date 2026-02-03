"""Add Persons Controller - Orchestrates adding new persons"""
from typing import Optional, Dict, Any

from app.services.add_persons import AddPersonsService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AddPersonsController:
    """Controller for adding persons to face recognition database"""
    
    def __init__(self, service: AddPersonsService = None):
        self.service = service or AddPersonsService()
    
    def add_persons(
        self, 
        source_path: Optional[str] = None,
        move_to_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Add persons from folder to database.
        
        Args:
            source_path: Optional path to folder with person subfolders
            move_to_backup: Whether to move processed folders to backup
        
        Returns:
            Response dict with results
        """
        result = self.service.add_persons_from_folder(source_path, move_to_backup)
        
        if result["success"]:
            logger.info(f"Added persons: {result['persons_added']}")
        else:
            logger.warning(f"Add persons failed: {result['message']}")
        
        return result
    
    def get_known_persons(self) -> Dict[str, Any]:
        """Get list of all known persons"""
        persons = self.service.list_known_persons()
        return {
            "success": True,
            "persons": persons,
            "count": len(persons)
        }
