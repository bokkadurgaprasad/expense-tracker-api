"""
Repository layer for MonthlySnapshot persistence
"""
from datetime import datetime, date
from bson import ObjectId
from typing import Optional, List


class MonthlySnapshotRepository:
    """MongoDB repository for monthly snapshots"""

    def __init__(self, database):
        self.collection = database.monthly_snapshots

    def _to_response(self, doc: dict) -> Optional[dict]:
        if not doc:
            return None
        out = dict(doc)
        out["_id"] = str(doc["_id"])
        out["user_id"] = str(doc["user_id"]) if isinstance(doc.get("user_id"), ObjectId) else doc["user_id"]
        if "snapshot_date" in out and hasattr(out["snapshot_date"], "isoformat"):
            v = out["snapshot_date"]
            out["snapshot_date"] = v.date().isoformat() if isinstance(v, datetime) else v.isoformat() if isinstance(v, date) else v
        return out

    def create(self, user_id: str, data: dict) -> dict:
        now = datetime.utcnow()
        snap_date = data["snapshot_date"]
        if isinstance(snap_date, date) and not isinstance(snap_date, datetime):
            snap_date = datetime(snap_date.year, snap_date.month, snap_date.day)
        doc = {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "snapshot_date": snap_date,
            "total_income": data["total_income"],
            "total_expenses": data["total_expenses"],
            "total_emi_paid": data["total_emi_paid"],
            "net_savings": data["net_savings"],
            "created_at": now,
        }
        self.collection.insert_one(doc)
        return self._to_response(doc)

    def find_by_user(self, user_id: str) -> List[dict]:
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("snapshot_date", -1)
        return [self._to_response(d) for d in cursor]
