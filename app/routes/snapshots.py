"""
API routes for MonthlySnapshot management
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
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


@router.get("", response_model=Dict[str, Any])
def get_snapshots(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id)
):
    """Get all monthly snapshots for the authenticated user with pagination"""
    service = MonthlySnapshotService()
    skip = (page - 1) * page_size
    return service.get_snapshots(user_id, skip, page_size)
