"""Abstract Repository Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IRepository(ABC):
    """
    Abstract base class for all repositories.
    Implements the Repository pattern for data access abstraction.
    """
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> str:
        """Create a new document and return its ID"""
        pass
    
    @abstractmethod
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the query"""
        pass
    
    @abstractmethod
    def find_many(
        self, 
        query: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find multiple documents matching the query"""
        pass
    
    @abstractmethod
    def update(
        self, 
        query: Dict[str, Any], 
        update_data: Dict[str, Any]
    ) -> bool:
        """Update documents matching the query"""
        pass
    
    @abstractmethod
    def delete(self, query: Dict[str, Any]) -> bool:
        """Delete documents matching the query"""
        pass
    
    @abstractmethod
    def count(self, query: Dict[str, Any]) -> int:
        """Count documents matching the query"""
        pass
