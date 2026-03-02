"""
Service layer for Dashboard data aggregation
"""
from datetime import datetime, timedelta
from typing import List
from app.services.financial_engine_service import FinancialEngineService
from app.services.credit_card_service import CreditCardService
from app.services.emi_service import EMIService
from app.services.borrow_service import BorrowService
from app.services.expected_cashflow_service import ExpectedCashflowService
from app.models.dashboard import DashboardData, UpcomingDue
from app.models.expected_cashflow import ExpectedCashflow


class DashboardService:
    """Service for dashboard data aggregation"""
    
    def __init__(self):
        self.financial_engine = FinancialEngineService()
        self.card_service = CreditCardService()
        self.emi_service = EMIService()
        self.borrow_service = BorrowService()
        self.cashflow_service = ExpectedCashflowService()
    
    def get_upcoming_dues(self, user_id: str, days: int = 7) -> List[UpcomingDue]:
        """Get all upcoming dues within specified days"""
        upcoming = []
        
        # Use naive datetime to match MongoDB storage
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today + timedelta(days=days)
        
        # Get pending expenses from cashflows (fetch all without pagination for dashboard)
        cashflows_data = self.cashflow_service.get_cashflows(user_id, skip=0, limit=1000)
        cashflows = cashflows_data["items"] if isinstance(cashflows_data, dict) else cashflows_data
        for cf in cashflows:
            if cf.transaction_type == "expense" and cf.status == "pending":
                # Ensure expected_date is naive datetime for comparison
                expected_date = cf.expected_date
                if expected_date.tzinfo is not None:
                    expected_date = expected_date.replace(tzinfo=None)
                
                if today <= expected_date <= end_date:
                    upcoming.append(UpcomingDue(
                        type="expense",
                        name=cf.description,
                        amount=cf.amount,
                        due_date=expected_date
                    ))
        
        # Get borrow records with upcoming due dates (fetch all without pagination for dashboard)
        borrows_data = self.borrow_service.get_borrows(user_id, skip=0, limit=1000)
        borrows = borrows_data["items"] if isinstance(borrows_data, dict) else borrows_data
        for borrow in borrows:
            if borrow.status == "active":
                # Ensure due_date is naive datetime for comparison
                due_date = borrow.due_date
                if due_date.tzinfo is not None:
                    due_date = due_date.replace(tzinfo=None)
                
                if today <= due_date <= end_date:
                    upcoming.append(UpcomingDue(
                        type="borrow",
                        name=f"{borrow.transaction_type}: {borrow.party_name}",
                        amount=borrow.remaining_amount,
                        due_date=due_date
                    ))
        
        # Sort by due date
        upcoming.sort(key=lambda x: x.due_date)
        return upcoming
    
    def get_missed_income(self, user_id: str) -> List[ExpectedCashflow]:
        """Get all missed income transactions"""
        cashflows_data = self.cashflow_service.get_cashflows(user_id, skip=0, limit=1000)
        cashflows = cashflows_data["items"] if isinstance(cashflows_data, dict) else cashflows_data
        missed = [
            cf for cf in cashflows
            if cf.transaction_type == "income" and cf.status == "missed"
        ]
        return missed
    
    def get_dashboard_data(self, user_id: str) -> DashboardData:
        """Get complete dashboard data"""
        metrics = self.financial_engine.get_financial_metrics(user_id)
        upcoming_dues = self.get_upcoming_dues(user_id, days=7)
        missed_income = self.get_missed_income(user_id)
        
        return DashboardData(
            metrics=metrics,
            upcoming_dues=upcoming_dues,
            missed_income=missed_income
        )
