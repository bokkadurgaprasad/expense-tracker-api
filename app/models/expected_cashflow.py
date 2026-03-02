"""
ExpectedCashflow model and schemas for expected income/expense management
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ExpectedCashflowBase(BaseModel):
    """Base ExpectedCashflow schema with common fields"""
    transaction_type: Literal["income", "expense"] = Field(..., description="Type of transaction")
    amount: float = Field(..., gt=0.0, description="Expected transaction amount")
    expected_date: datetime = Field(..., description="Expected date of the transaction")
    status: Literal["pending", "received", "missed"] = Field(..., description="Status of the cashflow")
    description: str = Field(..., min_length=1, max_length=200, description="Description of the cashflow")

    @field_validator('amount')
    @classmethod
    def validate_positive_amount(cls, v: float) -> float:
        """Validate that amount is positive"""
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class CashflowCreate(ExpectedCashflowBase):
    """Schema for creating a new expected cashflow"""
    pass


class CashflowUpdate(BaseModel):
    """Schema for updating an existing expected cashflow"""
    transaction_type: Optional[Literal["income", "expense"]] = Field(None, description="Type of transaction")
    amount: Optional[float] = Field(None, gt=0.0, description="Expected transaction amount")
    expected_date: Optional[datetime] = Field(None, description="Expected date of the transaction")
    status: Optional[Literal["pending", "received", "missed"]] = Field(None, description="Status of the cashflow")
    description: Optional[str] = Field(None, min_length=1, max_length=200, description="Description of the cashflow")

    @field_validator('amount')
    @classmethod
    def validate_positive_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate that amount is positive"""
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v


class ExpectedCashflow(ExpectedCashflowBase):
    """Complete ExpectedCashflow schema with all fields"""
    id: str = Field(..., alias="_id", description="Expected Cashflow ID")
    user_id: str = Field(..., description="Reference to User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "transaction_type": "income",
                "amount": 5000.00,
                "expected_date": "2024-12-31T00:00:00",
                "status": "pending",
                "description": "Monthly salary",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
