"""
Service layer for ExpectedCashflow business logic
"""
from typing import List
from fastapi import HTTPException
from app.repositories.expected_cashflow_repository import ExpectedCashflowRepository
from app.models.expected_cashflow import ExpectedCashflow, CashflowCreate, CashflowUpdate
from db.connection import get_database


class ExpectedCashflowService:
    """Service for ExpectedCashflow business logic"""
    
    def __init__(self):
        self.repo = ExpectedCashflowRepository(get_database())
    
    def create_cashflow(self, user_id: str, data: CashflowCreate) -> ExpectedCashflow:
        """Create a new expected cashflow"""
        cashflow_dict = self.repo.create(user_id, data.model_dump())
        return ExpectedCashflow(**cashflow_dict)
    
    def get_cashflows(self, user_id: str, skip: int = 0, limit: int = 10) -> dict:
        """Get all expected cashflows for a user with pagination"""
        cashflows, total_count = self.repo.find_by_user(user_id, skip, limit)
        return {
            "items": [ExpectedCashflow(**cf) for cf in cashflows],
            "total": total_count,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "page_size": limit,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
        }
    
    def get_missed_cashflows(self, user_id: str) -> List[ExpectedCashflow]:
        """Get all missed cashflows for a user"""
        cashflows = self.repo.find_missed(user_id)
        return [ExpectedCashflow(**cf) for cf in cashflows]
    
    def get_cashflow(self, user_id: str, cashflow_id: str) -> ExpectedCashflow:
        """Get a specific expected cashflow"""
        cashflow = self.repo.find_by_id(cashflow_id, user_id)
        if not cashflow:
            raise HTTPException(status_code=404, detail="Expected cashflow not found")
        return ExpectedCashflow(**cashflow)
    
    def update_cashflow(self, user_id: str, cashflow_id: str, data: CashflowUpdate) -> ExpectedCashflow:
        """Update an expected cashflow"""
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        cashflow = self.repo.update(cashflow_id, user_id, update_data)
        if not cashflow:
            raise HTTPException(status_code=404, detail="Expected cashflow not found")
        return ExpectedCashflow(**cashflow)
    
    def mark_as_received_or_paid(self, user_id: str, cashflow_id: str) -> ExpectedCashflow:
        """Mark cashflow as received (income) or paid (expense)"""
        # Get the cashflow to determine transaction type
        cashflow = self.repo.find_by_id(cashflow_id, user_id)
        if not cashflow:
            raise HTTPException(status_code=404, detail="Expected cashflow not found")
        
        updated = self.repo.mark_as_completed(cashflow_id, user_id, cashflow["transaction_type"])
        if not updated:
            raise HTTPException(status_code=404, detail="Expected cashflow not found")
        return ExpectedCashflow(**updated)
    
    def check_and_mark_missed(self, user_id: str) -> int:
        """Check and mark pending cashflows as missed if expected_date has passed"""
        return self.repo.check_and_mark_missed(user_id)
    
    def delete_cashflow(self, user_id: str, cashflow_id: str) -> bool:
        """Delete an expected cashflow"""
        deleted = self.repo.delete(cashflow_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Expected cashflow not found")
        return True
    
    def get_safe_expected_income(self, user_id: str) -> float:
        """Calculate safe expected income (pending income * 0.7)"""
        return self.repo.get_safe_expected_income(user_id)
    
    def get_pending_expenses(self, user_id: str) -> float:
        """Calculate total pending expenses"""
        return self.repo.get_pending_expenses(user_id)
