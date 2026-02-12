"""Student Log Repository - CRUD for student_logs collection"""
from typing import List, Dict, Any

from app.repositories.base import BaseRepository
from app.models.student_log import StudentLogDocument


class StudentLogRepository(BaseRepository):
    """Async repository for student field change audit logs."""
    
    def __init__(self):
        super().__init__(StudentLogDocument.collection_name)
    
    async def create_log(self, log_data: Dict[str, Any]) -> str:
        """Create a new student field change log entry."""
        return await self.create(log_data)
    
    async def get_logs_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all field change logs for a student."""
        return await self.find_many(
            {"student_id": student_id}, 
            limit=100
        )
