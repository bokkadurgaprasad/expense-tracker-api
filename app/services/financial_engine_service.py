"""
Service layer for Financial Engine calculations
"""
from app.services.bank_account_service import BankAccountService
from app.services.credit_card_service import CreditCardService
from app.services.emi_service import EMIService
from app.services.borrow_service import BorrowService
from app.services.expected_cashflow_service import ExpectedCashflowService
from app.models.financial_metrics import FinancialMetrics


class FinancialEngineService:
    """Service for financial calculations"""
    
    def __init__(self):
        self.bank_service = BankAccountService()
        self.card_service = CreditCardService()
        self.emi_service = EMIService()
        self.borrow_service = BorrowService()
        self.cashflow_service = ExpectedCashflowService()
    
    def calculate_total_liquid_balance(self, user_id: str) -> float:
        """Calculate total liquid balance minus reserves"""
        return self.bank_service.get_total_liquid_balance(user_id)
    
    def calculate_total_obligations(self, user_id: str) -> float:
        """Calculate total obligations from all sources"""
        credit_card_obligations = self.card_service.get_total_obligations(user_id)
        emi_obligations = self.emi_service.get_total_emi_obligations(user_id)
        borrowed_amount = self.borrow_service.get_total_borrowed(user_id)
        pending_expenses = self.cashflow_service.get_pending_expenses(user_id)
        
        return credit_card_obligations + emi_obligations + borrowed_amount + pending_expenses
    
    def calculate_safe_expected_income(self, user_id: str) -> float:
        """Calculate safe expected income (pending income * 0.7)"""
        return self.cashflow_service.get_safe_expected_income(user_id)
    
    def calculate_emergency_buffer(self, user_id: str) -> float:
        """Calculate emergency buffer (10% of total liquid balance)"""
        total_liquid = self.calculate_total_liquid_balance(user_id)
        return total_liquid * 0.1
    
    def calculate_safe_spendable_amount(self, user_id: str) -> float:
        """Calculate safe spendable amount"""
        total_liquid = self.calculate_total_liquid_balance(user_id)
        total_obligations = self.calculate_total_obligations(user_id)
        safe_income = self.calculate_safe_expected_income(user_id)
        emergency_buffer = self.calculate_emergency_buffer(user_id)
        
        return total_liquid + safe_income - total_obligations - emergency_buffer
    
    def get_financial_metrics(self, user_id: str) -> FinancialMetrics:
        """Get all financial metrics"""
        total_liquid = self.calculate_total_liquid_balance(user_id)
        total_obligations = self.calculate_total_obligations(user_id)
        safe_income = self.calculate_safe_expected_income(user_id)
        emergency_buffer = self.calculate_emergency_buffer(user_id)
        safe_spendable = self.calculate_safe_spendable_amount(user_id)
        net_position = total_liquid - total_obligations
        
        return FinancialMetrics(
            total_liquid_balance=total_liquid,
            total_obligations=total_obligations,
            safe_expected_income=safe_income,
            emergency_buffer=emergency_buffer,
            safe_spendable_amount=safe_spendable,
            net_position=net_position,
            total_liability=total_obligations
        )
