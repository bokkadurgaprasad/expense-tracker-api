"""
MonthlySnapshot model and schemas for monthly financial summary tracking
"""
from datetime import datetime, date
from calendar import monthrange
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class MonthlySnapshotBase(BaseModel):
    """Base MonthlySnapshot schema with common fields"""
    snapshot_date: date = Field(..., description="Last day of the month for this snapshot")
    total_income: float = Field(..., ge=0.0, description="Total income received during the month")
    total_expenses: float = Field(..., ge=0.0, description="Total expenses paid during the month")
    total_emi_paid: float = Field(..., ge=0.0, description="Total EMI payments made during the month")
    net_savings: float = Field(..., description="Net savings (income - expenses - emi_paid)")

    @field_validator('snapshot_date')
    @classmethod
    def validate_last_day_of_month(cls, v: date) -> date:
        """Validate that snapshot_date is the last day of the month"""
        # Get the last day of the month for the given date
        last_day = monthrange(v.year, v.month)[1]
        if v.day != last_day:
            raise ValueError(f'Snapshot date must be the last day of the month. Expected day {last_day}, got {v.day}')
        return v

    @field_validator('total_income', 'total_expenses', 'total_emi_paid')
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        """Validate that financial amounts are non-negative"""
        if v < 0:
            raise ValueError('Financial amounts must be non-negative')
        return v


class SnapshotCreate(BaseModel):
    """Schema for creating a new monthly snapshot"""
    snapshot_date: date = Field(..., description="Last day of the month for this snapshot")
    total_income: float = Field(..., ge=0.0, description="Total income received during the month")
    total_expenses: float = Field(..., ge=0.0, description="Total expenses paid during the month")
    total_emi_paid: float = Field(..., ge=0.0, description="Total EMI payments made during the month")

    @field_validator('snapshot_date')
    @classmethod
    def validate_last_day_of_month(cls, v: date) -> date:
        """Validate that snapshot_date is the last day of the month"""
        # Get the last day of the month for the given date
        last_day = monthrange(v.year, v.month)[1]
        if v.day != last_day:
            raise ValueError(f'Snapshot date must be the last day of the month. Expected day {last_day}, got {v.day}')
        return v

    @field_validator('total_income', 'total_expenses', 'total_emi_paid')
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        """Validate that financial amounts are non-negative"""
        if v < 0:
            raise ValueError('Financial amounts must be non-negative')
        return v


class MonthlySnapshot(MonthlySnapshotBase):
    """Complete MonthlySnapshot schema with all fields"""
    id: str = Field(..., alias="_id", description="Monthly Snapshot ID")
    user_id: str = Field(..., description="Reference to User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "snapshot_date": "2024-01-31",
                "total_income": 50000.00,
                "total_expenses": 30000.00,
                "total_emi_paid": 10000.00,
                "net_savings": 10000.00,
                "created_at": "2024-02-01T00:00:00"
            }
        }
