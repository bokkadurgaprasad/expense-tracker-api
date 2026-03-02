"""
Financial metrics computed response models
"""
from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    """Computed financial metrics (not stored in database)"""
    total_liquid_balance: float = Field(..., description="Sum of all bank account liquid balances minus reserves")
    total_obligations: float = Field(..., description="Sum of all credit card bills, EMIs, borrowed amounts, and pending expenses")
    safe_expected_income: float = Field(..., description="Sum of pending income multiplied by 0.7 safety factor")
    emergency_buffer: float = Field(..., description="10% of total liquid balance kept as emergency buffer")
    safe_spendable_amount: float = Field(..., description="Amount safe to spend after obligations and buffers")
    net_position: float = Field(..., description="Total liquid balance minus total obligations")
    total_liability: float = Field(..., description="Same as total obligations")

    class Config:
        json_schema_extra = {
            "example": {
                "total_liquid_balance": 10000.00,
                "total_obligations": 3000.00,
                "safe_expected_income": 2100.00,
                "emergency_buffer": 1000.00,
                "safe_spendable_amount": 8100.00,
                "net_position": 7000.00,
                "total_liability": 3000.00
            }
        }
