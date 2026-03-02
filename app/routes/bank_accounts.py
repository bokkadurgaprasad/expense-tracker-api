"""
API routes for BankAccount management
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.bank_account import BankAccount, BankAccountCreate, BankAccountUpdate
from app.services.bank_account_service import BankAccountService
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/bank-accounts", tags=["Bank Accounts"])


@router.post("", response_model=BankAccount, status_code=201)
def create_bank_account(
    data: BankAccountCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new bank account"""
    service = BankAccountService()
    return service.create_account(user_id, data)


@router.get("", response_model=Dict[str, Any])
def get_bank_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    user_id: str = Depends(get_current_user_id)
):
    """Get all bank accounts for the authenticated user with pagination"""
    service = BankAccountService()
    skip = (page - 1) * page_size
    return service.get_accounts(user_id, skip, page_size)


@router.get("/{account_id}", response_model=BankAccount)
def get_bank_account(
    account_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific bank account"""
    service = BankAccountService()
    return service.get_account(user_id, account_id)


@router.put("/{account_id}", response_model=BankAccount)
def update_bank_account(
    account_id: str,
    data: BankAccountUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update a bank account"""
    service = BankAccountService()
    return service.update_account(user_id, account_id, data)


@router.delete("/{account_id}", status_code=204)
def delete_bank_account(
    account_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a bank account"""
    service = BankAccountService()
    service.delete_account(user_id, account_id)
    return None
