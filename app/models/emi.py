"""
EMI model and schemas for loan EMI management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EMIBase(BaseModel):
    """Base EMI schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Loan name/description")
    principal_amount: float = Field(..., gt=0.0, description="Principal loan amount")
    interest_rate: float = Field(..., ge=0.0, description="Annual interest rate percentage")
    monthly_emi_amount: float = Field(..., gt=0.0, description="Monthly EMI payment amount")
    remaining_months: int = Field(..., ge=0, description="Number of months remaining")

    @field_validator('principal_amount', 'monthly_emi_amount')
    @classmethod
    def validate_positive_amounts(cls, v: float) -> float:
        """Validate that principal and EMI amounts are positive"""
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('interest_rate')
    @classmethod
    def validate_non_negative_rate(cls, v: float) -> float:
        """Validate that interest rate is non-negative"""
        if v < 0:
            raise ValueError('Interest rate must be non-negative')
        return v

    @field_validator('remaining_months')
    @classmethod
    def validate_non_negative_months(cls, v: int) -> int:
        """Validate that remaining months is non-negative"""
        if v < 0:
            raise ValueError('Remaining months must be non-negative')
        return v


class EMICreate(EMIBase):
    """Schema for creating a new EMI record"""
    pass


class EMIUpdate(BaseModel):
    """Schema for updating an existing EMI record"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Loan name/description")
    principal_amount: Optional[float] = Field(None, gt=0.0, description="Principal loan amount")
    interest_rate: Optional[float] = Field(None, ge=0.0, description="Annual interest rate percentage")
    monthly_emi_amount: Optional[float] = Field(None, gt=0.0, description="Monthly EMI payment amount")
    remaining_months: Optional[int] = Field(None, ge=0, description="Number of months remaining")

    @field_validator('principal_amount', 'monthly_emi_amount')
    @classmethod
    def validate_positive_amounts(cls, v: Optional[float]) -> Optional[float]:
        """Validate that principal and EMI amounts are positive"""
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('interest_rate')
    @classmethod
    def validate_non_negative_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate that interest rate is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Interest rate must be non-negative')
        return v

    @field_validator('remaining_months')
    @classmethod
    def validate_non_negative_months(cls, v: Optional[int]) -> Optional[int]:
        """Validate that remaining months is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Remaining months must be non-negative')
        return v


class EMI(EMIBase):
    """Complete EMI schema with all fields"""
    id: str = Field(..., alias="_id", description="EMI ID")
    user_id: str = Field(..., description="Reference to User ID")
    is_completed: bool = Field(default=False, description="True when remaining_months reaches 0")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "name": "Home Loan",
                "principal_amount": 500000.00,
                "interest_rate": 8.5,
                "monthly_emi_amount": 5000.00,
                "remaining_months": 120,
                "is_completed": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
