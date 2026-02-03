"""Recognition Repository for database operations"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.repositories.base import BaseRepository
from app.schemas import RecognitionLogSchema
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecognitionRepository(BaseRepository):
    """Repository for recognition logs"""
    
    def __init__(self):
        """Initialize recognition repository"""
        super().__init__(RecognitionLogSchema.collection_name)
    
    def create_or_update_log(self, person_name: str, camera_id: str,
                            confidence_score: Optional[float] = None) -> str:
        """
        Create or update recognition log with 1-hour cooldown.
        Returns log ID.
        """
        # Look for existing log within 1 hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        query = {
            "person_name": person_name,
            "camera_id": camera_id,
            "last_detection_time": {"$gte": one_hour_ago}
        }
        
        existing_log = self.find_one(query)
        
        if existing_log:
            # Update existing log - increment counter and update timestamp
            log_id = str(existing_log["_id"])
            self.increment(log_id, "detection_count", 1)
            self.update(log_id, {
                "last_detection_time": datetime.utcnow(),
                "confidence_score": confidence_score
            })
            logger.info(f"Updated log for {person_name} at camera {camera_id}")
            return log_id
        else:
            # Create new log
            doc = RecognitionLogSchema.get_document(
                person_name, camera_id, confidence_score
            )
            log_id = self.create(doc)
            logger.info(f"Created new log for {person_name} at camera {camera_id}")
            return log_id
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get recognition log by ID"""
        return self.find_by_id(log_id)
    
    def get_logs_with_filter(self, person_name: Optional[str] = None,
                            camera_id: Optional[str] = None,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recognition logs with filtering"""
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
        
        return self.find_many(query, skip, limit)
    
    def update_log(self, log_id: str, person_name: Optional[str] = None,
                  camera_id: Optional[str] = None,
                  confidence_score: Optional[float] = None) -> bool:
        """Update recognition log"""
        update_data = {}
        
        if person_name is not None:
            update_data["person_name"] = person_name
        if camera_id is not None:
            update_data["camera_id"] = camera_id
        if confidence_score is not None:
            update_data["confidence_score"] = confidence_score
        
        if not update_data:
            return False
        
        return self.update(log_id, update_data)
    
    def delete_log(self, log_id: str) -> bool:
        """Delete recognition log"""
        return self.delete(log_id)
    
    def get_all_logs(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all recognition logs with pagination"""
        return self.find_many({}, skip, limit)
    
    def get_total_count(self, person_name: Optional[str] = None,
                       camera_id: Optional[str] = None) -> int:
        """Get total count of logs with optional filtering"""
        query = {}
        
        if person_name:
            query["person_name"] = {"$regex": person_name, "$options": "i"}
        
        if camera_id:
            query["camera_id"] = {"$regex": camera_id, "$options": "i"}
        
        return self.count(query)
