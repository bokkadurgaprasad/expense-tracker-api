"""
Service layer for EMI business logic
"""
from typing import List
from fastapi import HTTPException
from app.repositories.emi_repository import EMIRepository
from app.models.emi import EMI, EMICreate, EMIUpdate
from db.connection import get_database


class EMIService:
    """Service for EMI business logic"""
    
    def __init__(self):
        self.repo = EMIRepository(get_database())
    
    def create_emi(self, user_id: str, data: EMICreate) -> EMI:
        """Create a new EMI record"""
        emi_dict = self.repo.create(user_id, data.model_dump())
        return EMI(**emi_dict)
    
    def get_emis(self, user_id: str, skip: int = 0, limit: int = 10) -> dict:
        """Get all EMI records for a user with pagination"""
        emis, total_count = self.repo.find_by_user(user_id, skip, limit)
        return {
            "items": [EMI(**emi) for emi in emis],
            "total": total_count,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "page_size": limit,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
        }
    
    def get_emi(self, user_id: str, emi_id: str) -> EMI:
        """Get a specific EMI record"""
        emi = self.repo.find_by_id(emi_id, user_id)
        if not emi:
            raise HTTPException(status_code=404, detail="EMI record not found")
        return EMI(**emi)
    
    def mark_payment_completed(self, user_id: str, emi_id: str) -> EMI:
        """Mark EMI payment as completed (decrement remaining_months)"""
        emi = self.repo.mark_payment_completed(emi_id, user_id)
        if not emi:
            raise HTTPException(status_code=404, detail="EMI record not found")
        return EMI(**emi)
    
    def update_emi(self, user_id: str, emi_id: str, data: EMIUpdate) -> EMI:
        """Update an EMI record"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Auto-complete if remaining_months is set to 0
        if "remaining_months" in update_data and update_data["remaining_months"] == 0:
            update_data["is_completed"] = True
        
        emi = self.repo.update(emi_id, user_id, update_data)
        if not emi:
            raise HTTPException(status_code=404, detail="EMI record not found")
        return EMI(**emi)
    
    def delete_emi(self, user_id: str, emi_id: str) -> bool:
        """Delete an EMI record"""
        deleted = self.repo.delete(emi_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="EMI record not found")
        return True
    
    def get_total_emi_obligations(self, user_id: str) -> float:
        """Calculate total EMI obligations (only active EMIs)"""
        return self.repo.get_total_emi_obligations(user_id)
