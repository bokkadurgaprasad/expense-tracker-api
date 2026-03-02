"""
Repository layer for BankAccount persistence
"""
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Any


class BankAccountRepository:
    """MongoDB repository for bank accounts"""

    def __init__(self, database):
        self.collection = database.bank_accounts

    def _to_response(self, doc: dict) -> dict:
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
            "bank_name": data["bank_name"],
            "liquid_balance": data["liquid_balance"],
            "reserve_amount": data["reserve_amount"],
            "created_at": now,
            "updated_at": now,
        }
        self.collection.insert_one(doc)
        return self._to_response(doc)

    def find_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> tuple[List[dict], int]:
        """
        Find bank accounts by user with pagination
        Returns: (accounts_list, total_count)
        """
        query = {"user_id": ObjectId(user_id)}
        total_count = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        accounts = [self._to_response(d) for d in cursor]
        return accounts, total_count

    def find_by_id(self, account_id: str, user_id: str) -> Optional[dict]:
        try:
            doc = self.collection.find_one({
                "_id": ObjectId(account_id),
                "user_id": ObjectId(user_id)
            })
            return self._to_response(doc) if doc else None
        except Exception:
            return None

    def update(self, account_id: str, user_id: str, update_data: dict) -> Optional[dict]:
        if not update_data:
            return None
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(account_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        return self._to_response(result) if result else None

    def delete(self, account_id: str, user_id: str) -> bool:
        result = self.collection.delete_one({
            "_id": ObjectId(account_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0

    def get_total_liquid_balance(self, user_id: str) -> float:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$project": {"net": {"$subtract": ["$liquid_balance", "$reserve_amount"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$net"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        return float(result[0]["total"]) if result else 0.0
