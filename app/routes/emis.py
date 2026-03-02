"""
API routes for EMI management
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from app.models.emi import EMI, EMICreate, EMIUpdate
from app.services.emi_service import EMIService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/emis", tags=["EMIs"])


@router.post("", response_model=EMI, status_code=201)
def create_emi(
    data: EMICreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new EMI record"""
    service = EMIService()
    return service.create_emi(user_id, data)


@router.get("", response_model=Dict[str, Any])
def get_emis(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id)
):
    """Get all EMI records for the authenticated user with pagination"""
    service = EMIService()
    skip = (page - 1) * page_size
    return service.get_emis(user_id, skip, page_size)


@router.get("/{emi_id}", response_model=EMI)
def get_emi(
    emi_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific EMI record"""
    service = EMIService()
    return service.get_emi(user_id, emi_id)


@router.post("/{emi_id}/mark-payment", response_model=EMI)
def mark_emi_payment(
    emi_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Mark EMI payment as completed (decrement remaining_months)"""
    service = EMIService()
    return service.mark_payment_completed(user_id, emi_id)


@router.put("/{emi_id}", response_model=EMI)
def update_emi(
    emi_id: str,
    data: EMIUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update an EMI record"""
    service = EMIService()
    return service.update_emi(user_id, emi_id, data)


@router.delete("/{emi_id}", status_code=204)
def delete_emi(
    emi_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an EMI record"""
    service = EMIService()
    service.delete_emi(user_id, emi_id)
    return None
