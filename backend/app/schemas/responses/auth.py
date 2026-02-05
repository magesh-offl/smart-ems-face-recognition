"""Auth Response Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime


class TokenResponse(BaseModel):
    """Response schema for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class APIKeyResponse(BaseModel):
    """Response schema for API key"""
    id: str = Field(alias="_id")
    name: str
    key: str
    created_at: datetime
    
    class Config:
        populate_by_name = True
    
    @staticmethod
    def from_mongo(doc):
        """Convert MongoDB document to APIKeyResponse"""
        if not doc:
            return None
        return APIKeyResponse(
            _id=str(doc.get('_id')),
            name=doc.get('name'),
            key=doc.get('key'),
            created_at=doc.get('created_at')
        )
