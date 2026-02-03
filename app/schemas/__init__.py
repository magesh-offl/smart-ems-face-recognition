"""MongoDB Collection Schemas"""
from datetime import datetime
from typing import Optional


class RecognitionLogSchema:
    """MongoDB schema for recognition logs"""
    collection_name = "recognition_logs"
    
    @staticmethod
    def get_document(person_name: str, camera_id: str, 
                    confidence_score: Optional[float] = None):
        """Get MongoDB document structure"""
        return {
            "person_name": person_name,
            "camera_id": camera_id,
            "timestamp": datetime.utcnow(),
            "confidence_score": confidence_score,
            "detection_count": 1,
            "last_detection_time": datetime.utcnow(),
        }


class UserSchema:
    """MongoDB schema for users"""
    collection_name = "users"
    
    @staticmethod
    def get_document(username: str, hashed_password: str):
        """Get MongoDB document structure"""
        return {
            "username": username,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }


class APIKeySchema:
    """MongoDB schema for API keys"""
    collection_name = "api_keys"
    
    @staticmethod
    def get_document(name: str, key: str, description: Optional[str] = None):
        """Get MongoDB document structure"""
        return {
            "name": name,
            "key": key,
            "description": description,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }
