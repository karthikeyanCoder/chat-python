from datetime import datetime


class PaymentsRepository:
    def __init__(self, db_instance):
        self.db = db_instance
        # Use the get_collection method or direct access
        import os
        db_name = os.getenv("DB_NAME", "patients_db")
        self.collection = db_instance.client[db_name].payments if db_instance.client else None

    def insert_payment(self, doc: dict):
        if self.collection is None:
            return None
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def update_payment_by_id(self, _id, update: dict):
        if self.collection is None:
            return False
        from bson import ObjectId
        res = self.collection.update_one({"_id": ObjectId(_id)}, {"$set": {**update, "updatedAt": datetime.utcnow()}})
        return res.modified_count > 0

    def update_payment_by_order_id(self, razorpay_order_id, update: dict):
        if self.collection is None:
            return False
        res = self.collection.update_one({"razorpayOrderId": razorpay_order_id}, {"$set": {**update, "updatedAt": datetime.utcnow()}})
        return res.modified_count > 0

    def find_by_id_or_order_id(self, payment_id: str, razorpay_order_id: str):
        if self.collection is None:
            return None
        from bson import ObjectId
        doc = None
        try:
            doc = self.collection.find_one({"_id": ObjectId(payment_id)})
        except Exception:
            pass
        if not doc and razorpay_order_id:
            doc = self.collection.find_one({"razorpayOrderId": razorpay_order_id})
        return doc

    def list_user_payments(self, username: str):
        if self.collection is None:
            return []
        items = list(self.collection.find({"userName": username}).sort("createdAt", -1))
        for p in items:
            p["_id"] = str(p["_id"])
            for k in ("createdAt", "updatedAt", "validityStartDate", "validityEndDate"):
                if p.get(k):
                    p[k] = p[k].isoformat()
        return items

    def latest_paid(self, username: str):
        if self.collection is None:
            return None
        return self.collection.find_one({"userName": username, "status": "paid"}, sort=[("createdAt", -1)])
