"""
Service layer for CreditCard business logic
"""
from typing import List
from fastapi import HTTPException
from app.repositories.credit_card_repository import CreditCardRepository
from app.repositories.bank_account_repository import BankAccountRepository
from app.models.credit_card import CreditCard, CreditCardCreate, CreditCardUpdate
from db.connection import get_database


class CreditCardService:
    """Service for CreditCard business logic"""
    
    def __init__(self):
        self.repo = CreditCardRepository(get_database())
        self.bank_repo = BankAccountRepository(get_database())
    
    def create_card(self, user_id: str, data: CreditCardCreate) -> CreditCard:
        """Create a new credit card"""
        # Validate bank_account_id exists and belongs to user
        bank_account = self.bank_repo.find_by_id(data.bank_account_id, user_id)
        if not bank_account:
            raise HTTPException(status_code=400, detail="Invalid bank_account_id or account does not belong to user")
        
        card_dict = self.repo.create(user_id, data.model_dump())
        return CreditCard(**card_dict)
    
    def get_cards(self, user_id: str, skip: int = 0, limit: int = 10) -> dict:
        """Get all credit cards for a user with pagination"""
        cards, total_count = self.repo.find_by_user(user_id, skip, limit)
        return {
            "items": [CreditCard(**card) for card in cards],
            "total": total_count,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "page_size": limit,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
        }
    
    def get_card(self, user_id: str, card_id: str) -> CreditCard:
        """Get a specific credit card"""
        card = self.repo.find_by_id(card_id, user_id)
        if not card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        return CreditCard(**card)
    
    def update_card(self, user_id: str, card_id: str, data: CreditCardUpdate) -> CreditCard:
        """Update a credit card"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Validate bank_account_id if being updated
        if "bank_account_id" in update_data:
            bank_account = self.bank_repo.find_by_id(update_data["bank_account_id"], user_id)
            if not bank_account:
                raise HTTPException(status_code=400, detail="Invalid bank_account_id or account does not belong to user")
        
        card = self.repo.update(card_id, user_id, update_data)
        if not card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        return CreditCard(**card)
    
    def delete_card(self, user_id: str, card_id: str) -> bool:
        """Delete a credit card"""
        deleted = self.repo.delete(card_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Credit card not found")
        return True
    
    def get_total_obligations(self, user_id: str) -> float:
        """Calculate total credit card obligations"""
        return self.repo.get_total_obligations(user_id)
