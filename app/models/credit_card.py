"""
CreditCard model and schemas for credit card management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreditCardBase(BaseModel):
    """Base CreditCard schema with common fields"""
    card_name: str = Field(..., min_length=1, max_length=100, description="Name of the credit card")
    bank_account_id: str = Field(..., description="Reference to linked BankAccount ID")
    current_spend: float = Field(..., ge=0.0, description="Unbilled spend amount")
    billed_amount: float = Field(..., ge=0.0, description="Amount billed and due")
    emi_due: float = Field(..., ge=0.0, description="EMI amount due on this card")

    @field_validator('current_spend', 'billed_amount', 'emi_due')
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        """Validate that all amounts are non-negative"""
        if v < 0:
            raise ValueError('Amount must be non-negative')
        return v


class CreditCardCreate(CreditCardBase):
    """Schema for creating a new credit card"""
    pass


class CreditCardUpdate(BaseModel):
    """Schema for updating an existing credit card"""
    card_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the credit card")
    bank_account_id: Optional[str] = Field(None, description="Reference to linked BankAccount ID")
    current_spend: Optional[float] = Field(None, ge=0.0, description="Unbilled spend amount")
    billed_amount: Optional[float] = Field(None, ge=0.0, description="Amount billed and due")
    emi_due: Optional[float] = Field(None, ge=0.0, description="EMI amount due on this card")

    @field_validator('current_spend', 'billed_amount', 'emi_due')
    @classmethod
    def validate_non_negative(cls, v: Optional[float]) -> Optional[float]:
        """Validate that all amounts are non-negative"""
        if v is not None and v < 0:
            raise ValueError('Amount must be non-negative')
        return v


class CreditCard(CreditCardBase):
    """Complete CreditCard schema with all fields"""
    id: str = Field(..., alias="_id", description="Credit Card ID")
    user_id: str = Field(..., description="Reference to User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "card_name": "Chase Sapphire",
                "bank_account_id": "507f1f77bcf86cd799439013",
                "current_spend": 1500.00,
                "billed_amount": 3000.00,
                "emi_due": 500.00,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
