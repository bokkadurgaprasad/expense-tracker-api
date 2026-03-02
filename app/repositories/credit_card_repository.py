"""
Repository layer for CreditCard persistence
"""
from datetime import datetime
from bson import ObjectId
from typing import Optional, List


class CreditCardRepository:
    """MongoDB repository for credit cards"""

    def __init__(self, database):
        self.collection = database.credit_cards

    def _to_response(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        out = dict(doc)
        out["_id"] = str(doc["_id"])
        out["user_id"] = str(doc["user_id"]) if isinstance(doc.get("user_id"), ObjectId) else doc["user_id"]
        out["bank_account_id"] = str(doc["bank_account_id"]) if isinstance(doc.get("bank_account_id"), ObjectId) else doc["bank_account_id"]
        return out

    def create(self, user_id: str, data: dict) -> dict:
        now = datetime.utcnow()
        doc = {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "bank_account_id": ObjectId(data["bank_account_id"]),
            "card_name": data["card_name"],
            "current_spend": data["current_spend"],
            "billed_amount": data["billed_amount"],
            "emi_due": data["emi_due"],
            "created_at": now,
            "updated_at": now,
        }
        self.collection.insert_one(doc)
        return self._to_response(doc)

    def find_by_user(self, user_id: str) -> List[dict]:
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        return [self._to_response(d) for d in cursor]

    def find_by_id(self, card_id: str, user_id: str) -> Optional[dict]:
        try:
            doc = self.collection.find_one({
                "_id": ObjectId(card_id),
                "user_id": ObjectId(user_id)
            })
            return self._to_response(doc) if doc else None
        except Exception:
            return None

    def update(self, card_id: str, user_id: str, update_data: dict) -> Optional[dict]:
        if not update_data:
            return None
        if "bank_account_id" in update_data and isinstance(update_data["bank_account_id"], str):
            update_data["bank_account_id"] = ObjectId(update_data["bank_account_id"])
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(card_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        return self._to_response(result) if result else None

    def delete(self, card_id: str, user_id: str) -> bool:
        result = self.collection.delete_one({
            "_id": ObjectId(card_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0

    def get_total_obligations(self, user_id: str) -> float:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$project": {"total": {"$add": ["$current_spend", "$billed_amount", "$emi_due"]}}},
            {"$group": {"_id": None, "sum": {"$sum": "$total"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        return float(result[0]["sum"]) if result else 0.0
