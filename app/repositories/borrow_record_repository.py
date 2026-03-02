"""
Repository layer for BorrowRecord persistence
"""
from datetime import datetime
from bson import ObjectId
from typing import Optional, List


class BorrowRecordRepository:
    """MongoDB repository for borrow records"""

    def __init__(self, database):
        self.collection = database.borrow_records

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
            "party_name": data["party_name"],
            "transaction_type": data["transaction_type"],
            "remaining_amount": data["remaining_amount"],
            "due_date": data["due_date"],
            "status": data["status"],
            "created_at": now,
            "updated_at": now,
        }
        self.collection.insert_one(doc)
        return self._to_response(doc)

    def find_by_user(self, user_id: str) -> List[dict]:
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        return [self._to_response(d) for d in cursor]

    def find_by_id(self, borrow_id: str, user_id: str) -> Optional[dict]:
        try:
            doc = self.collection.find_one({
                "_id": ObjectId(borrow_id),
                "user_id": ObjectId(user_id)
            })
            return self._to_response(doc) if doc else None
        except Exception:
            return None

    def update(self, borrow_id: str, user_id: str, update_data: dict) -> Optional[dict]:
        if not update_data:
            return None
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(borrow_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        return self._to_response(result) if result else None

    def delete(self, borrow_id: str, user_id: str) -> bool:
        result = self.collection.delete_one({
            "_id": ObjectId(borrow_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0

    def get_total_borrowed(self, user_id: str) -> float:
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id), "transaction_type": "borrowed_from", "status": "active"}},
            {"$group": {"_id": None, "total": {"$sum": "$remaining_amount"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        return float(result[0]["total"]) if result else 0.0
