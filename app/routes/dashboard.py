"""
API routes for Dashboard data
"""
from fastapi import APIRouter, Depends
from app.models.dashboard import DashboardData
from app.services.dashboard_service import DashboardService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardData)
def get_dashboard(user_id: str = Depends(get_current_user_id)):
    """Get complete dashboard data"""
    service = DashboardService()
    return service.get_dashboard_data(user_id)
