"""
API routes for MonthlySnapshot management
"""
from typing import List
from fastapi import APIRouter, Depends
from app.models.monthly_snapshot import MonthlySnapshot, SnapshotCreate
from app.services.monthly_snapshot_service import MonthlySnapshotService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/snapshots", tags=["Monthly Snapshots"])


@router.post("", response_model=MonthlySnapshot, status_code=201)
def create_snapshot(
    data: SnapshotCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new monthly snapshot"""
    service = MonthlySnapshotService()
    return service.create_snapshot(user_id, data)


@router.get("", response_model=List[MonthlySnapshot])
def get_snapshots(user_id: str = Depends(get_current_user_id)):
    """Get all monthly snapshots for the authenticated user"""
    service = MonthlySnapshotService()
    return service.get_snapshots(user_id)
