"""
MongoDB data layer.

Collections
  found_items : reports of items people have found
  lost_items  : reports of items people have lost
  counters    : auto-increment report numbers (1, 2, 3 ...) that are easy to read

Every report looks like:
  {report_no, category, description, location, date (YYYY-MM-DD),
   contact, status ("Open" / "Returned"), created_at}
"""

import csv
from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient, ReturnDocument

FOUND = "found_items"
LOST = "lost_items"


class Database:
    def __init__(self, uri=None, db_name="lost_and_found", client=None):
        # `client` lets tests pass in a fake client (mongomock)
        self.client = client or MongoClient(uri, serverSelectionTimeoutMS=8000)
        self.db = self.client[db_name]

    # ---------- connection ----------
    def ping(self):
        """Raises an error if MongoDB cannot be reached."""
        self.client.admin.command("ping")

    def setup(self, found_csv=None, lost_csv=None):
        """Create indexes and load sample data the first time (empty database)."""
        for name in (FOUND, LOST):
            self.db[name].create_index([("report_no", ASCENDING)], unique=True)
        if found_csv and self.db[FOUND].count_documents({}) == 0:
            self._seed(FOUND, found_csv)
        if lost_csv and self.db[LOST].count_documents({}) == 0:
            self._seed(LOST, lost_csv)

    def _seed(self, collection, csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self._insert(collection, {
                    "category": row["category"],
                    "description": row["description"],
                    "location": row["location"],
                    "date": row["date"],
                    "contact": row.get("contact") or "Lost & Found office",
                })

    # ---------- helpers ----------
    def _next_number(self, collection):
        counter = self.db["counters"].find_one_and_update(
            {"_id": collection}, {"$inc": {"seq": 1}},
            upsert=True, return_document=ReturnDocument.AFTER,
        )
        return counter["seq"]

    def _insert(self, collection, data):
        doc = {
            "report_no": self._next_number(collection),
            "category": data["category"],
            "description": data["description"].strip(),
            "location": data["location"].strip(),
            "date": data["date"],
            "contact": (data.get("contact") or "").strip(),
            "status": "Open",
            "created_at": datetime.now(timezone.utc),
        }
        self.db[collection].insert_one(doc)
        return doc["report_no"]

    @staticmethod
    def _clean(doc):
        """MongoDB document -> plain dict used by the algorithms ('id' = report number)."""
        return {
            "id": doc["report_no"],
            "category": doc["category"],
            "description": doc["description"],
            "location": doc["location"],
            "date": doc["date"],
            "contact": doc.get("contact", ""),
            "status": doc.get("status", "Open"),
        }

    def _list(self, collection, status=None):
        query = {"status": status} if status else {}
        cursor = self.db[collection].find(query).sort("report_no", ASCENDING)
        return [self._clean(d) for d in cursor]

    # ---------- public API ----------
    def add_found(self, data):
        return self._insert(FOUND, data)

    def add_lost(self, data):
        return self._insert(LOST, data)

    def get_found(self, status=None):
        return self._list(FOUND, status)

    def get_lost(self, status=None):
        return self._list(LOST, status)

    def set_status(self, kind, report_no, status):
        collection = FOUND if kind == "found" else LOST
        self.db[collection].update_one({"report_no": report_no}, {"$set": {"status": status}})

    def delete(self, kind, report_no):
        collection = FOUND if kind == "found" else LOST
        self.db[collection].delete_one({"report_no": report_no})

    def counts(self):
        return {
            "found_open": self.db[FOUND].count_documents({"status": "Open"}),
            "lost_open": self.db[LOST].count_documents({"status": "Open"}),
            "returned": self.db[FOUND].count_documents({"status": "Returned"}),
        }
