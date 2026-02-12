"""
Database Seeder Service.

This module provides a service layer for database seeding operations.
Following MVC + Layered + Dependency Injection architecture:

- Fixtures: Static data definitions (core/fixtures.py)
- SeederService: Orchestrates seeding logic with injected repositories
- CLI Script: Runs seeder from command line (scripts/seed_db.py)

Usage:
    # Via dependency injection
    seeder = SeederService(course_repo=CourseRepository())
    await seeder.seed_all()
    
    # Via CLI
    python -m scripts.seed_db
"""
import logging
from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# =============================================
# Repository Protocol (for DI)
# =============================================

class CourseRepositoryProtocol(Protocol):
    """Protocol defining the interface for course repository."""
    
    async def get_by_course_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get course by course_id."""
        ...
    
    async def create_course(self, course_data: Dict[str, Any]) -> str:
        """Create a new course."""
        ...


# =============================================
# Base Seeder Interface
# =============================================

class BaseSeeder(ABC):
    """Abstract base class for seeders."""
    
    @abstractmethod
    async def seed(self) -> int:
        """Run seeding. Returns number of records created."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Return count of seeded items already in database."""
        pass


# =============================================
# Course Seeder
# =============================================

class CourseSeeder(BaseSeeder):
    """Seeder for courses collection."""
    
    def __init__(self, course_repo: CourseRepositoryProtocol):
        self.course_repo = course_repo
        self._fixtures: list = []
    
    def with_fixtures(self, fixtures: list) -> 'CourseSeeder':
        """Set fixtures data. Fluent interface."""
        self._fixtures = fixtures
        return self
    
    async def seed(self) -> int:
        """Seed courses from fixtures.
        
        Returns:
            Number of courses created
        """
        from app.models import CourseDocument
        
        created_count = 0
        
        for course_data in self._fixtures:
            # Check if already exists
            existing = await self.course_repo.get_by_course_id(course_data["course_id"])
            if existing:
                logger.debug(f"Course {course_data['course_id']} already exists, skipping")
                continue
            
            # Create document
            doc = CourseDocument.create(
                course_id=course_data["course_id"],
                name=course_data["name"],
                section=course_data["section"],
                description=course_data.get("description", ""),
                is_active=True
            )
            
            try:
                await self.course_repo.create_course(doc)
                created_count += 1
                logger.info(f"Created course: {course_data['course_id']} - {course_data['name']} {course_data['section']}")
            except Exception as e:
                logger.error(f"Failed to create course {course_data['course_id']}: {e}")
        
        return created_count
    
    async def count(self) -> int:
        """Count courses that already exist."""
        count = 0
        for course_data in self._fixtures:
            existing = await self.course_repo.get_by_course_id(course_data["course_id"])
            if existing:
                count += 1
        return count


# =============================================
# Main Seeder Service (Facade)
# =============================================

class SeederService:
    """
    Main seeder service that orchestrates all seeders.
    
    Follows Dependency Injection pattern by accepting repositories
    rather than instantiating them directly.
    
    Usage:
        from app.repositories.course import CourseRepository
        
        seeder = SeederService(course_repo=CourseRepository())
        results = await seeder.seed_all()
    """
    
    def __init__(
        self,
        course_repo: Optional[CourseRepositoryProtocol] = None
    ):
        self.course_repo = course_repo
        self._seeders: Dict[str, BaseSeeder] = {}
        self._setup_seeders()
    
    def _setup_seeders(self) -> None:
        """Initialize seeders with injected dependencies."""
        from app.core.fixtures import COURSES
        
        if self.course_repo:
            self._seeders["courses"] = CourseSeeder(self.course_repo).with_fixtures(COURSES)
    
    async def seed_all(self) -> Dict[str, int]:
        """Run all seeders.
        
        Returns:
            Dictionary mapping seeder name to number of records created
        """
        results = {}
        
        for name, seeder in self._seeders.items():
            try:
                count = await seeder.seed()
                results[name] = count
                if count > 0:
                    logger.info(f"Seeded {count} {name}")
                else:
                    logger.info(f"All {name} already seeded")
            except Exception as e:
                logger.error(f"Failed to seed {name}: {e}")
                results[name] = -1  # Indicate error
        
        return results
    
    async def seed_courses(self) -> int:
        """Seed only courses."""
        if "courses" in self._seeders:
            return await self._seeders["courses"].seed()
        return 0
    
    async def status(self) -> Dict[str, Dict[str, int]]:
        """Get seeding status for all seeders.
        
        Returns:
            Dictionary with total and existing counts for each seeder
        """
        from app.core.fixtures import COURSES
        
        status = {}
        
        if "courses" in self._seeders:
            existing = await self._seeders["courses"].count()
            status["courses"] = {
                "total": len(COURSES),
                "existing": existing,
                "pending": len(COURSES) - existing
            }
        
        return status


# =============================================
# Factory function for DI container integration
# =============================================

def get_seeder_service() -> SeederService:
    """Factory function to create SeederService with default dependencies.
    
    This can be used with FastAPI's Depends() or for manual instantiation.
    """
    from app.repositories.course import CourseRepository
    
    return SeederService(
        course_repo=CourseRepository()
    )
