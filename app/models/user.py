"""
User model and schemas for authentication
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    """Base User schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters and underscores"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v.lower()


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100, description="User password")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Schema for user authentication"""
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Normalize username to lowercase for case-insensitive login"""
        return v.lower()


class PasswordReset(BaseModel):
    """Schema for password reset"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class User(UserBase):
    """Complete User schema with all fields"""
    id: str = Field(..., alias="_id", description="User ID")
    password_hash: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "password_hash": "$2b$12$...",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: str = Field(..., alias="_id", description="User ID")
    username: str = Field(..., description="Username")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        populate_by_name = True
