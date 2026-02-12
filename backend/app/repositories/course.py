"""Course Repository - CRUD for courses collection"""
from typing import List, Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import CourseDocument


class CourseRepository(BaseRepository):
    """Async repository for course management."""
    
    def __init__(self):
        super().__init__(CourseDocument.collection_name)
    
    async def create_course(self, course_data: Dict[str, Any]) -> str:
        """Create a new course."""
        return await self.create(course_data)
    
    async def get_by_course_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get course by semantic course_id (e.g., CRS0001)."""
        return await self.find_one({"course_id": course_id})
    
    async def get_by_name_section(self, name: str, section: str) -> Optional[Dict[str, Any]]:
        """Get course by name and section."""
        return await self.find_one({"name": name, "section": section})
    
    async def get_all_courses(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all courses, optionally filtered by active status."""
        query = {"is_active": True} if active_only else {}
        return await self.find_many(query, limit=1000)
    
    async def get_courses_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Get all sections for a course name."""
        return await self.find_many({"name": name}, limit=100)
    
    async def course_exists(self, course_id: str) -> bool:
        """Check if course exists by course_id."""
        return await self.find_one({"course_id": course_id}) is not None
    
    async def update_course(self, course_id: str, data: Dict[str, Any]) -> bool:
        """Update course by course_id."""
        course = await self.get_by_course_id(course_id)
        if course:
            return await self.update(str(course["_id"]), data)
        return False
