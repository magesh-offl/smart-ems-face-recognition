"""Async Batch Recognition Repository"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.repositories.base import BaseRepository
from app.models import BatchRecognitionLogDocument


class BatchRecognitionRepository(BaseRepository):
    """Async repository for batch recognition logs."""
    
    def __init__(self):
        super().__init__(BatchRecognitionLogDocument.collection_name)
    
    async def save_batch_logs(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Save multiple detection logs at once."""
        if not logs:
            return []
        coll = await self._get_collection()
        result = await coll.insert_many(logs)
        return [str(id) for id in result.inserted_ids]
    
    async def update_log(self, log_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a batch recognition log with additional data."""
        coll = await self._get_collection()
        result = await coll.update_one(
            {"_id": ObjectId(log_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def get_logs_by_batch_id(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific batch."""
        return await self.find_many({"batch_id": batch_id}, skip=0, limit=100)
    
    async def get_logs_with_filters(
        self,
        student_id: Optional[str] = None,
        course_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recognition logs with optional filters for history panel."""
        query: Dict[str, Any] = {}
        
        if student_id:
            query["student_id"] = {"$regex": student_id, "$options": "i"}
        
        if course_id:
            query["course_id"] = course_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["detection_datetime"] = date_query
        
        coll = await self._get_collection()
        cursor = coll.find(query).sort("detection_datetime", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count_logs_with_filters(
        self,
        student_id: Optional[str] = None,
        course_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count logs matching filters."""
        query: Dict[str, Any] = {}
        
        if student_id:
            query["student_id"] = {"$regex": student_id, "$options": "i"}
        
        if course_id:
            query["course_id"] = course_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["detection_datetime"] = date_query
        
        coll = await self._get_collection()
        return await coll.count_documents(query)
    
    async def get_batch_summary(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a batch."""
        logs = await self.get_logs_by_batch_id(batch_id)
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
    
    async def get_all_batches(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unique batch summaries with pagination."""
        coll = await self._get_collection()
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
        cursor = coll.aggregate(pipeline)
        return await cursor.to_list(length=limit)
    
    async def delete_all(self) -> int:
        """Delete all batch recognition logs."""
        coll = await self._get_collection()
        result = await coll.delete_many({})
        return result.deleted_count

