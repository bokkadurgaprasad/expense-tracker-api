"""
Service layer for MonthlySnapshot business logic
"""
from typing import List
from datetime import date
from calendar import monthrange
from bson import ObjectId
from app.repositories.monthly_snapshot_repository import MonthlySnapshotRepository
from app.models.monthly_snapshot import MonthlySnapshot, SnapshotCreate
from db.connection import get_database


class MonthlySnapshotService:
    """Service for MonthlySnapshot business logic"""
    
    def __init__(self):
        self.repo = MonthlySnapshotRepository(get_database())
        self.db = get_database()
    
    def calculate_monthly_income(self, user_id: str, month: date) -> float:
        """Calculate total income received for a given month"""
        start_date = date(month.year, month.month, 1)
        last_day = monthrange(month.year, month.month)[1]
        end_date = date(month.year, month.month, last_day)
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "transaction_type": "income",
                    "status": "received",
                    "expected_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        result = list(self.db["expected_cashflows"].aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    
    def calculate_monthly_expenses(self, user_id: str, month: date) -> float:
        """Calculate total expenses paid for a given month"""
        start_date = date(month.year, month.month, 1)
        last_day = monthrange(month.year, month.month)[1]
        end_date = date(month.year, month.month, last_day)
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "transaction_type": "expense",
                    "status": {"$in": ["received", "paid"]},  # Accept both for expenses
                    "expected_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        result = list(self.db["expected_cashflows"].aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    
    def calculate_monthly_emi_paid(self, user_id: str, month: date) -> float:
        """Calculate total EMI paid for a given month (simplified - returns sum of active EMIs)"""
        # Note: This is a simplified implementation
        # In a real system, you'd track actual EMI payments with timestamps
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "is_completed": False
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$monthly_emi_amount"}}}
        ]
        
        result = list(self.db["emis"].aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    
    def create_snapshot(self, user_id: str, data: SnapshotCreate) -> MonthlySnapshot:
        """Create a new monthly snapshot"""
        # Calculate net savings
        net_savings = data.total_income - data.total_expenses - data.total_emi_paid
        
        snapshot_data = {
            **data.model_dump(),
            "net_savings": net_savings
        }
        
        snapshot_dict = self.repo.create(user_id, snapshot_data)
        return MonthlySnapshot(**snapshot_dict)
    
    def get_snapshots(self, user_id: str) -> List[MonthlySnapshot]:
        """Get all monthly snapshots for a user, ordered by date"""
        snapshots = self.repo.find_by_user(user_id)
        return [MonthlySnapshot(**snap) for snap in snapshots]
