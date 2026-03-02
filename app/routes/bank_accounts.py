"""
API routes for BankAccount management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
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


@router.get("", response_model=List[BankAccount])
def get_bank_accounts(user_id: str = Depends(get_current_user_id)):
    """Get all bank accounts for the authenticated user"""
    service = BankAccountService()
    return service.get_accounts(user_id)


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
