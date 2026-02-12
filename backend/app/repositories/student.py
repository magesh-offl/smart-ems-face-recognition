"""Student Repository - CRUD for students collection"""
from typing import List, Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import StudentDocument


class StudentRepository(BaseRepository):
    """Async repository for student management."""
    
    def __init__(self):
        super().__init__(StudentDocument.collection_name)
    
    async def create_student(self, student_data: Dict[str, Any]) -> str:
        """Create a new student."""
        return await self.create(student_data)
    
    async def get_by_student_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get student by semantic student_id (e.g., STU260030001)."""
        return await self.find_one({"student_id": student_id})
    
    async def get_by_user_ref(self, user_ref: str) -> Optional[Dict[str, Any]]:
        """Get student by user reference (MongoDB _id)."""
        return await self.find_one({"user_ref": user_ref})
    
    async def get_by_guardian_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get student by guardian phone number."""
        return await self.find_one({"guardian_phone": phone})
    
    async def get_students_by_course(
        self, 
        course_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get students by current course."""
        return await self.find_many(
            {"current_course_id": course_id}, 
            skip=skip, 
            limit=limit
        )
    
    async def get_untrained_students(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get students without face training."""
        return await self.find_many({"is_trained": False}, limit=limit)
    
    async def update_trained_status(self, student_id: str, is_trained: bool) -> bool:
        """Update face training status."""
        student = await self.get_by_student_id(student_id)
        if student:
            return await self.update(str(student["_id"]), {"is_trained": is_trained})
        return False
    
    async def update_course(self, student_id: str, new_course_id: str) -> bool:
        """Update student's current course (for promotions)."""
        student = await self.get_by_student_id(student_id)
        if student:
            return await self.update(str(student["_id"]), {"current_course_id": new_course_id})
        return False
    
    async def student_exists(self, student_id: str) -> bool:
        """Check if student exists by student_id."""
        return await self.find_one({"student_id": student_id}) is not None
    
    async def count_by_course(self, course_id: str) -> int:
        """Count students in a course."""
        return await self.count({"current_course_id": course_id})
    
    async def update_student(self, student_id: str, update_data: Dict[str, Any]) -> bool:
        """Update student fields by student_id.
        
        Args:
            student_id: Student's semantic ID
            update_data: Dict of fields to update
            
        Returns:
            True if updated successfully
        """
        student = await self.get_by_student_id(student_id)
        if student:
            from app.models.base import BaseDocument
            update_data.update(BaseDocument.update_timestamp())
            return await self.update(str(student["_id"]), update_data)
        return False

