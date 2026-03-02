"""
BankAccount model and schemas for bank account management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BankAccountBase(BaseModel):
    """Base BankAccount schema with common fields"""
    bank_name: str = Field(..., min_length=1, max_length=100, description="Name of the bank")
    liquid_balance: float = Field(..., ge=0.0, description="Current available balance")
    reserve_amount: float = Field(..., ge=0.0, description="Amount to keep as reserve (not spendable)")

    @field_validator('liquid_balance', 'reserve_amount')
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        """Validate that balance and reserve amounts are non-negative"""
        if v < 0:
            raise ValueError('Amount must be non-negative')
        return v


class BankAccountCreate(BankAccountBase):
    """Schema for creating a new bank account"""
    pass


class BankAccountUpdate(BaseModel):
    """Schema for updating an existing bank account"""
    bank_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the bank")
    liquid_balance: Optional[float] = Field(None, ge=0.0, description="Current available balance")
    reserve_amount: Optional[float] = Field(None, ge=0.0, description="Amount to keep as reserve")

    @field_validator('liquid_balance', 'reserve_amount')
    @classmethod
    def validate_non_negative(cls, v: Optional[float]) -> Optional[float]:
        """Validate that balance and reserve amounts are non-negative"""
        if v is not None and v < 0:
            raise ValueError('Amount must be non-negative')
        return v


class BankAccount(BankAccountBase):
    """Complete BankAccount schema with all fields"""
    id: str = Field(..., alias="_id", description="Bank Account ID")
    user_id: str = Field(..., description="Reference to User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "bank_name": "Chase Bank",
                "liquid_balance": 5000.00,
                "reserve_amount": 1000.00,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
