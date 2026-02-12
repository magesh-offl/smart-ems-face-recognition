"""Admission Repository - CRUD for admissions collection"""
from typing import List, Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import AdmissionDocument


class AdmissionRepository(BaseRepository):
    """Async repository for admission management."""
    
    def __init__(self):
        super().__init__(AdmissionDocument.collection_name)
    
    async def create_admission(self, admission_data: Dict[str, Any]) -> str:
        """Create a new admission record."""
        return await self.create(admission_data)
    
    async def get_by_admission_id(self, admission_id: str) -> Optional[Dict[str, Any]]:
        """Get admission by semantic admission_id (e.g., ADMN26030001)."""
        return await self.find_one({"admission_id": admission_id})
    
    async def get_by_student_id(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all admissions for a student (history)."""
        return await self.find_many({"student_id": student_id}, limit=100)
    
    async def get_current_admission(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get current active admission for a student."""
        return await self.find_one({
            "student_id": student_id, 
            "status": AdmissionDocument.STATUS_ACTIVE
        })
    
    async def get_admissions_by_course(
        self, 
        course_id: str, 
        academic_year: Optional[str] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get admissions by course and optionally academic year."""
        query = {"course_id": course_id, "status": AdmissionDocument.STATUS_ACTIVE}
        if academic_year:
            query["academic_year"] = academic_year
        return await self.find_many(query, skip=skip, limit=limit)
    
    async def update_status(self, admission_id: str, status: str) -> bool:
        """Update admission status (promote, withdraw, graduate)."""
        admission = await self.get_by_admission_id(admission_id)
        if admission:
            return await self.update(str(admission["_id"]), {"status": status})
        return False
    
    async def count_by_course_year(self, course_id: str, academic_year: str) -> int:
        """Count admissions for a course in an academic year."""
        return await self.count({
            "course_id": course_id, 
            "academic_year": academic_year
        })
    
    async def update_admission(self, admission_id: str, update_data: Dict[str, Any]) -> bool:
        """Update admission fields (e.g., student_id, course_id on course transfer).
        
        Args:
            admission_id: The admission's semantic ID
            update_data: Dict of fields to update
            
        Returns:
            True if updated successfully
        """
        admission = await self.get_by_admission_id(admission_id)
        if admission:
            from app.models.base import BaseDocument
            update_data.update(BaseDocument.update_timestamp())
            return await self.update(str(admission["_id"]), update_data)
        return False

