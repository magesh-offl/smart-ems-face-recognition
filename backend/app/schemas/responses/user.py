"""User Response Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime


class UserResponse(BaseModel):
    """Response schema for user data"""
    id: str = Field(alias="_id")
    username: str
    created_at: datetime
    
    class Config:
        populate_by_name = True
    
    @staticmethod
    def from_mongo(doc):
        """Convert MongoDB document to UserResponse"""
        if not doc:
            return None
        return UserResponse(
            _id=str(doc.get('_id')),
            username=doc.get('username'),
            created_at=doc.get('created_at')
        )
