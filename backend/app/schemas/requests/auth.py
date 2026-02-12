"""Auth Request Schemas"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Schema for user registration with role support"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    email: EmailStr
    role_id: str = Field(default="ROL0004", description="Default: student role")
    first_name: str = Field(default="", max_length=50)
    last_name: str = Field(default="", max_length=50)


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    username: str = Field(..., min_length=1)


class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
