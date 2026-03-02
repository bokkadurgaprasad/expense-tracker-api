"""
Dashboard data computed response models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from .financial_metrics import FinancialMetrics
from .expected_cashflow import ExpectedCashflow


class UpcomingDue(BaseModel):
    """Model for upcoming due items"""
    type: str = Field(..., description="Type of due: credit_card, emi, borrow, or expense")
    name: str = Field(..., description="Name or description of the due item")
    amount: float = Field(..., description="Amount due")
    due_date: datetime = Field(..., description="Date when payment is due")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "credit_card",
                "name": "Chase Visa",
                "amount": 1500.00,
                "due_date": "2024-01-15T00:00:00"
            }
        }


class DashboardData(BaseModel):
    """Complete dashboard data with metrics, upcoming dues, and missed income"""
    metrics: FinancialMetrics = Field(..., description="Computed financial metrics")
    upcoming_dues: List[UpcomingDue] = Field(default_factory=list, description="Dues within the next 7 days")
    missed_income: List[ExpectedCashflow] = Field(default_factory=list, description="Missed expected income transactions")

    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "total_liquid_balance": 10000.00,
                    "total_obligations": 3000.00,
                    "safe_expected_income": 2100.00,
                    "emergency_buffer": 1000.00,
                    "safe_spendable_amount": 8100.00,
                    "net_position": 7000.00,
                    "total_liability": 3000.00
                },
                "upcoming_dues": [
                    {
                        "type": "credit_card",
                        "name": "Chase Visa",
                        "amount": 1500.00,
                        "due_date": "2024-01-15T00:00:00"
                    }
                ],
                "missed_income": []
            }
        }
