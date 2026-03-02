"""
API routes for Financial Engine calculations
"""
from fastapi import APIRouter, Depends
from app.models.financial_metrics import FinancialMetrics
from app.services.financial_engine_service import FinancialEngineService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/financial-engine", tags=["Financial Engine"])


@router.get("/metrics", response_model=FinancialMetrics)
def get_financial_metrics(user_id: str = Depends(get_current_user_id)):
    """Get all financial metrics"""
    service = FinancialEngineService()
    return service.get_financial_metrics(user_id)


@router.get("/safe-spendable")
def get_safe_spendable(user_id: str = Depends(get_current_user_id)):
    """Get safe spendable amount"""
    service = FinancialEngineService()
    amount = service.calculate_safe_spendable_amount(user_id)
    return {"safe_spendable_amount": amount}
