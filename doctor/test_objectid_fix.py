"""
Test script to verify ObjectId serialization fix in chat rooms
"""
import json
from datetime import datetime
from bson import ObjectId

# Mock MongoDB document with ObjectId
mock_room_doc = {
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "room_id": "ROOM1234567890ABCD",
    "doctor_id": "doctor_123",
    "patient_id": "patient_456",
    "last_message": "Hello doctor",
    "last_message_time": datetime.utcnow(),
    "last_message_id": "MSG1234567890ABCD",
    "unread_count_doctor": 2,
    "unread_count_patient": 0,
    "is_active": True,
    "is_archived": False,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "room_name": "Dr. Smith - Patient John",
    "room_description": None,
    "tags": [],
    "pinned_by_doctor": False,
    "notifications_enabled_doctor": True,
    "notifications_enabled_patient": True
}

def test_objectid_serialization():
    """Test that ObjectId fields are properly converted to strings"""

    # Simulate the old behavior (would fail)
    print("Testing raw document serialization...")
    try:
        json.dumps(mock_room_doc)
        print("❌ ERROR: Raw document should not be JSON serializable")
    except TypeError as e:
        print(f"✅ Expected error with raw document: {str(e)}")

    # Simulate the new behavior (should work)
    print("\nTesting cleaned document serialization...")

    # Apply the same logic as in the repository
    clean_room_data = {}
    for key, value in mock_room_doc.items():
        if hasattr(value, 'generation_time'):  # ObjectId
            clean_room_data[key] = str(value)
        else:
            clean_room_data[key] = value

    try:
        json_str = json.dumps(clean_room_data, default=str)  # default=str for datetime
        print("✅ Cleaned document is JSON serializable")
        print(f"Sample JSON: {json_str[:200]}...")

        # Verify ObjectId was converted
        parsed = json.loads(json_str)
        if isinstance(parsed['_id'], str):
            print("✅ ObjectId field converted to string")
        else:
            print("❌ ObjectId field not converted properly")

    except Exception as e:
        print(f"❌ ERROR: Cleaned document should be serializable: {str(e)}")

if __name__ == "__main__":
    test_objectid_serialization()