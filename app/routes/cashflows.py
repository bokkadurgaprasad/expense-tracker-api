"""
API routes for ExpectedCashflow management
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from app.models.expected_cashflow import ExpectedCashflow, CashflowCreate, CashflowUpdate
from app.services.expected_cashflow_service import ExpectedCashflowService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/cashflows", tags=["Expected Cashflows"])


@router.post("", response_model=ExpectedCashflow, status_code=201)
def create_cashflow(
    data: CashflowCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new expected cashflow"""
    service = ExpectedCashflowService()
    return service.create_cashflow(user_id, data)


@router.get("", response_model=Dict[str, Any])
def get_cashflows(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id)
):
    """Get all expected cashflows for the authenticated user with pagination"""
    service = ExpectedCashflowService()
    skip = (page - 1) * page_size
    return service.get_cashflows(user_id, skip, page_size)


@router.get("/missed", response_model=List[ExpectedCashflow])
def get_missed_cashflows(user_id: str = Depends(get_current_user_id)):
    """Get all missed cashflows for the authenticated user"""
    service = ExpectedCashflowService()
    return service.get_missed_cashflows(user_id)


@router.get("/{cashflow_id}", response_model=ExpectedCashflow)
def get_cashflow(
    cashflow_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific expected cashflow"""
    service = ExpectedCashflowService()
    return service.get_cashflow(user_id, cashflow_id)


@router.post("/{cashflow_id}/mark-completed", response_model=ExpectedCashflow)
def mark_cashflow_completed(
    cashflow_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Mark cashflow as received (income) or paid (expense)"""
    service = ExpectedCashflowService()
    return service.mark_as_received_or_paid(user_id, cashflow_id)


@router.put("/{cashflow_id}", response_model=ExpectedCashflow)
def update_cashflow(
    cashflow_id: str,
    data: CashflowUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update an expected cashflow"""
    service = ExpectedCashflowService()
    return service.update_cashflow(user_id, cashflow_id, data)


@router.delete("/{cashflow_id}", status_code=204)
def delete_cashflow(
    cashflow_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an expected cashflow"""
    service = ExpectedCashflowService()
    service.delete_cashflow(user_id, cashflow_id)
    return None
