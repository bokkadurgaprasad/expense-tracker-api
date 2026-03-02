"""
Service layer for BankAccount business logic
"""
from typing import List
from fastapi import HTTPException
from app.repositories.bank_account_repository import BankAccountRepository
from app.models.bank_account import BankAccount, BankAccountCreate, BankAccountUpdate
from db.connection import get_database


class BankAccountService:
    """Service for BankAccount business logic"""
    
    def __init__(self):
        self.repo = BankAccountRepository(get_database())
    
    def create_account(self, user_id: str, data: BankAccountCreate) -> BankAccount:
        """Create a new bank account"""
        account_dict = self.repo.create(user_id, data.model_dump())
        return BankAccount(**account_dict)
    
    def get_accounts(self, user_id: str) -> List[BankAccount]:
        """Get all bank accounts for a user"""
        accounts = self.repo.find_by_user(user_id)
        return [BankAccount(**acc) for acc in accounts]
    
    def get_account(self, user_id: str, account_id: str) -> BankAccount:
        """Get a specific bank account"""
        account = self.repo.find_by_id(account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        return BankAccount(**account)
    
    def update_account(self, user_id: str, account_id: str, data: BankAccountUpdate) -> BankAccount:
        """Update a bank account"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        account = self.repo.update(account_id, user_id, update_data)
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        return BankAccount(**account)
    
    def delete_account(self, user_id: str, account_id: str) -> bool:
        """Delete a bank account"""
        deleted = self.repo.delete(account_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Bank account not found")
        return True
    
    def get_total_liquid_balance(self, user_id: str) -> float:
        """Calculate total liquid balance minus reserves"""
        return self.repo.get_total_liquid_balance(user_id)
