"""Batch Recognition Repository"""
from typing import List, Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import BatchRecognitionLogDocument


class BatchRecognitionRepository(BaseRepository):
    """Repository for batch recognition logs."""
    
    def __init__(self):
        super().__init__(BatchRecognitionLogDocument.collection_name)
    
    def save_batch_logs(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Save multiple detection logs at once."""
        if not logs:
            return []
        result = self.collection.insert_many(logs)
        return [str(id) for id in result.inserted_ids]
    
    def get_logs_by_batch_id(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific batch."""
        return self.find_many({"batch_id": batch_id}, skip=0, limit=100)
    
    def get_batch_summary(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a batch."""
        logs = self.get_logs_by_batch_id(batch_id)
        if not logs:
            return None
        first = logs[0]
        return {
            "batch_id": batch_id,
            "source_path": first.get("source_path"),
            "total_faces_detected": first.get("total_faces_detected", 0),
            "recognized_count": len(logs),
            "processing_time_ms": first.get("processing_time_ms"),
            "logs": logs
        }
    
    def get_all_batches(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unique batch summaries with pagination."""
        pipeline = [
            {"$group": {
                "_id": "$batch_id",
                "source_path": {"$first": "$source_path"},
                "detection_datetime": {"$first": "$detection_datetime"},
                "total_faces_detected": {"$first": "$total_faces_detected"},
                "recognized_count": {"$sum": 1},
                "processing_time_ms": {"$first": "$processing_time_ms"}
            }},
            {"$sort": {"detection_datetime": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        return list(self.collection.aggregate(pipeline))
    
    def delete_all(self) -> int:
        """Delete all batch recognition logs."""
        return self.collection.delete_many({}).deleted_count
