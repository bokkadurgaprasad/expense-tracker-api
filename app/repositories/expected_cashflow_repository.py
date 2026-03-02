"""
Repository layer for ExpectedCashflow persistence
"""
from datetime import datetime
from bson import ObjectId
from typing import Optional, List


class ExpectedCashflowRepository:
    """MongoDB repository for expected cashflows"""

    def __init__(self, database):
        self.collection = database.expected_cashflows

    def _to_response(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        out = dict(doc)
        out["_id"] = str(doc["_id"])
        out["user_id"] = str(doc["user_id"]) if isinstance(doc.get("user_id"), ObjectId) else doc["user_id"]
        return out

    def create(self, user_id: str, data: dict) -> dict:
        now = datetime.utcnow()
        doc = {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "transaction_type": data["transaction_type"],
            "amount": data["amount"],
            "expected_date": data["expected_date"],
            "status": data["status"],
            "description": data["description"],
            "created_at": now,
            "updated_at": now,
        }
        self.collection.insert_one(doc)
        return self._to_response(doc)

    def find_by_user(self, user_id: str) -> List[dict]:
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        return [self._to_response(d) for d in cursor]

    def find_by_id(self, cashflow_id: str, user_id: str) -> Optional[dict]:
        try:
            doc = self.collection.find_one({
                "_id": ObjectId(cashflow_id),
                "user_id": ObjectId(user_id)
            })
            return self._to_response(doc) if doc else None
        except Exception:
            return None

    def find_missed(self, user_id: str) -> List[dict]:
        cursor = self.collection.find({"user_id": ObjectId(user_id), "status": "missed"})
        return [self._to_response(d) for d in cursor]

    def update(self, cashflow_id: str, user_id: str, update_data: dict) -> Optional[dict]:
        if not update_data:
            return None
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(cashflow_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        return self._to_response(result) if result else None

    def delete(self, cashflow_id: str, user_id: str) -> bool:
        result = self.collection.delete_one({
            "_id": ObjectId(cashflow_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0

    def mark_as_completed(self, cashflow_id: str, user_id: str, transaction_type: str) -> Optional[dict]:
        status_value = "received" if transaction_type == "income" else "paid"
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(cashflow_id), "user_id": ObjectId(user_id)},
            {"$set": {"status": status_value, "updated_at": datetime.utcnow()}},
            return_document=True
        )
        return self._to_response(result) if result else None

    def check_and_mark_missed(self, user_id: str) -> int:
        result = self.collection.update_many(
            {"user_id": ObjectId(user_id), "status": "pending", "expected_date": {"$lt": datetime.utcnow()}},
            {"$set": {"status": "missed", "updated_at": datetime.utcnow()}}
        )
        return result.modified_count

    def get_safe_expected_income(self, user_id: str) -> float:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id), "transaction_type": "income", "status": "pending"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        return float(result[0]["total"] * 0.7) if result else 0.0

    def get_pending_expenses(self, user_id: str) -> float:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id), "transaction_type": "expense", "status": "pending"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        return float(result[0]["total"]) if result else 0.0
