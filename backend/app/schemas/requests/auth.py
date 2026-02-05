"""Auth Request Schemas"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
