"""
BorrowRecord model and schemas for borrow/lend transaction management
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class BorrowRecordBase(BaseModel):
    """Base BorrowRecord schema with common fields"""
    party_name: str = Field(..., min_length=1, max_length=100, description="Name of the person/entity")
    transaction_type: Literal["borrowed_from", "lent_to"] = Field(..., description="Type of transaction")
    remaining_amount: float = Field(..., ge=0.0, description="Remaining amount to be paid/received")
    due_date: datetime = Field(..., description="Due date for the transaction")
    status: Literal["active", "completed"] = Field(..., description="Status of the borrow record")

    @field_validator('remaining_amount')
    @classmethod
    def validate_non_negative_amount(cls, v: float) -> float:
        """Validate that remaining amount is non-negative"""
        if v < 0:
            raise ValueError('Remaining amount must be non-negative')
        return v


class BorrowCreate(BorrowRecordBase):
    """Schema for creating a new borrow record"""
    pass


class BorrowUpdate(BaseModel):
    """Schema for updating an existing borrow record"""
    party_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the person/entity")
    transaction_type: Optional[Literal["borrowed_from", "lent_to"]] = Field(None, description="Type of transaction")
    remaining_amount: Optional[float] = Field(None, ge=0.0, description="Remaining amount to be paid/received")
    due_date: Optional[datetime] = Field(None, description="Due date for the transaction")
    status: Optional[Literal["active", "completed"]] = Field(None, description="Status of the borrow record")

    @field_validator('remaining_amount')
    @classmethod
    def validate_non_negative_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate that remaining amount is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Remaining amount must be non-negative')
        return v


class BorrowRecord(BorrowRecordBase):
    """Complete BorrowRecord schema with all fields"""
    id: str = Field(..., alias="_id", description="Borrow Record ID")
    user_id: str = Field(..., description="Reference to User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "party_name": "John Doe",
                "transaction_type": "borrowed_from",
                "remaining_amount": 5000.00,
                "due_date": "2024-12-31T00:00:00",
                "status": "active",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
