"""
API routes for BorrowRecord management
"""
from typing import List
from fastapi import APIRouter, Depends
from app.models.borrow_record import BorrowRecord, BorrowCreate, BorrowUpdate
from app.services.borrow_service import BorrowService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/borrows", tags=["Borrow Records"])


@router.post("", response_model=BorrowRecord, status_code=201)
def create_borrow(
    data: BorrowCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new borrow record"""
    service = BorrowService()
    return service.create_borrow(user_id, data)


@router.get("", response_model=List[BorrowRecord])
def get_borrows(user_id: str = Depends(get_current_user_id)):
    """Get all borrow records for the authenticated user"""
    service = BorrowService()
    return service.get_borrows(user_id)


@router.get("/{borrow_id}", response_model=BorrowRecord)
def get_borrow(
    borrow_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific borrow record"""
    service = BorrowService()
    return service.get_borrow(user_id, borrow_id)


@router.put("/{borrow_id}", response_model=BorrowRecord)
def update_borrow(
    borrow_id: str,
    data: BorrowUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update a borrow record"""
    service = BorrowService()
    return service.update_borrow(user_id, borrow_id, data)


@router.delete("/{borrow_id}", status_code=204)
def delete_borrow(
    borrow_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a borrow record"""
    service = BorrowService()
    service.delete_borrow(user_id, borrow_id)
    return None
