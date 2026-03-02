"""
Service layer for BorrowRecord business logic
"""
from typing import List
from fastapi import HTTPException
from app.repositories.borrow_record_repository import BorrowRecordRepository
from app.models.borrow_record import BorrowRecord, BorrowCreate, BorrowUpdate
from db.connection import get_database


class BorrowService:
    """Service for BorrowRecord business logic"""
    
    def __init__(self):
        self.repo = BorrowRecordRepository(get_database())
    
    def create_borrow(self, user_id: str, data: BorrowCreate) -> BorrowRecord:
        """Create a new borrow record"""
        borrow_dict = self.repo.create(user_id, data.model_dump())
        return BorrowRecord(**borrow_dict)
    
    def get_borrows(self, user_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a user"""
        borrows = self.repo.find_by_user(user_id)
        return [BorrowRecord(**borrow) for borrow in borrows]
    
    def get_borrow(self, user_id: str, borrow_id: str) -> BorrowRecord:
        """Get a specific borrow record"""
        borrow = self.repo.find_by_id(borrow_id, user_id)
        if not borrow:
            raise HTTPException(status_code=404, detail="Borrow record not found")
        return BorrowRecord(**borrow)
    
    def update_borrow(self, user_id: str, borrow_id: str, data: BorrowUpdate) -> BorrowRecord:
        """Update a borrow record"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        borrow = self.repo.update(borrow_id, user_id, update_data)
        if not borrow:
            raise HTTPException(status_code=404, detail="Borrow record not found")
        return BorrowRecord(**borrow)
    
    def delete_borrow(self, user_id: str, borrow_id: str) -> bool:
        """Delete a borrow record"""
        deleted = self.repo.delete(borrow_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Borrow record not found")
        return True
    
    def get_total_borrowed(self, user_id: str) -> float:
        """Calculate total borrowed amount (active borrowed_from records)"""
        return self.repo.get_total_borrowed(user_id)
