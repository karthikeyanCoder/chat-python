#!/usr/bin/env python3
"""
Database Setup Test Script
Tests the availability database setup
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_availability_database():
    """Test availability database setup"""
    try:
        from models.database import Database
        
        print("🧪 Testing availability database setup...")
        
        # Initialize database
        db = Database()
        if not db.connect():
            print("❌ Database connection failed")
            return False
        
        print("✅ Database connected successfully")
        
        # Test collection creation
        test_doc = {
            "test": True,
            "timestamp": datetime.now(),
            "doctor_id": "TEST_DOC",
            "date": "2025-10-26"
        }
        
        print("🧪 Testing availability collection...")
        result = db.doctor_availability_collection.insert_one(test_doc)
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Test retrieval
        retrieved = db.doctor_availability_collection.find_one({"_id": result.inserted_id})
        if retrieved:
            print("✅ Document retrieved successfully")
            print(f"   - Doctor ID: {retrieved['doctor_id']}")
            print(f"   - Date: {retrieved['date']}")
            print(f"   - Test: {retrieved['test']}")
        
        # Test indexes
        print("🧪 Testing indexes...")
        indexes = list(db.doctor_availability_collection.list_indexes())
        print(f"✅ Found {len(indexes)} indexes:")
        for index in indexes:
            print(f"   - {index['name']}: {index['key']}")
        
        # Clean up
        db.doctor_availability_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        print("✅ Database setup test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_availability_database()
    if success:
        print("\n🎉 Database setup test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database setup test failed!")
        sys.exit(1)
