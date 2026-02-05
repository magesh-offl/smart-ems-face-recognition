"""Async Recognition Repository"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.repositories.base import BaseRepository
from app.models import RecognitionLogDocument


class RecognitionRepository(BaseRepository):
    """Async repository for recognition logs."""
    
    def __init__(self):
        super().__init__(RecognitionLogDocument.collection_name)
    
    async def create_or_update_log(self, person_name: str, camera_id: str,
                                   confidence_score: Optional[float] = None) -> str:
        """Create or update recognition log with 1-hour cooldown."""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        query = {
            "person_name": person_name,
            "camera_id": camera_id,
            "last_detection_time": {"$gte": one_hour_ago}
        }
        
        existing = await self.find_one(query)
        if existing:
            log_id = str(existing["_id"])
            await self.increment(log_id, "detection_count", 1)
            await self.update(log_id, {
                "last_detection_time": datetime.utcnow(),
                "confidence_score": confidence_score
            })
            return log_id
        
        doc = RecognitionLogDocument.create(person_name, camera_id, confidence_score)
        return await self.create(doc)
    
    async def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get recognition log by ID."""
        return await self.find_by_id(log_id)
    
    async def get_logs_with_filter(self, person_name: Optional[str] = None,
                                   camera_id: Optional[str] = None,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None,
                                   skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recognition logs with filtering."""
        query = {}
        if person_name:
            query["person_name"] = {"$regex": person_name, "$options": "i"}
        if camera_id:
            query["camera_id"] = {"$regex": camera_id, "$options": "i"}
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["timestamp"] = date_query
        return await self.find_many(query, skip, limit)
    
    async def update_log(self, log_id: str, person_name: Optional[str] = None,
                        camera_id: Optional[str] = None,
                        confidence_score: Optional[float] = None) -> bool:
        """Update recognition log."""
        data = {}
        if person_name is not None:
            data["person_name"] = person_name
        if camera_id is not None:
            data["camera_id"] = camera_id
        if confidence_score is not None:
            data["confidence_score"] = confidence_score
        return await self.update(log_id, data) if data else False
    
    async def delete_log(self, log_id: str) -> bool:
        """Delete recognition log."""
        return await self.delete(log_id)
    
    async def get_all_logs(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all recognition logs with pagination."""
        return await self.find_many({}, skip, limit)
    
    async def get_total_count(self, person_name: Optional[str] = None,
                              camera_id: Optional[str] = None) -> int:
        """Get total count of logs with optional filtering."""
        query = {}
        if person_name:
            query["person_name"] = {"$regex": person_name, "$options": "i"}
        if camera_id:
            query["camera_id"] = {"$regex": camera_id, "$options": "i"}
        return await self.count(query)
