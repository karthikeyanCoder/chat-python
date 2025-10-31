#!/usr/bin/env python3
"""
Script to create a test doctor account in the database
"""

import os
import sys
import hashlib
from datetime import datetime
from bson import ObjectId

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database
from models.doctor_model import DoctorModel

def create_test_doctor():
    """Create test doctor account"""
    try:
        # Initialize database
        db = Database()
        if not db.connect():
            print("❌ Failed to connect to database")
            return False
            
        doctor_model = DoctorModel(db)
        
        # Test doctor data
        test_doctor = {
            'username': 'testdoctor',
            'email': 'doctor@test.com',
            'mobile': '1234567890',
            'password': 'password123',
            'role': 'doctor',
            'is_verified': True,  # Skip OTP verification
            'created_at': datetime.now().isoformat()
        }
        
        # Create doctor
        result = doctor_model.create_doctor(test_doctor)
        
        if result['success']:
            print("✅ Test doctor created successfully")
            print(f"Email: {test_doctor['email']}")
            print(f"Password: {test_doctor['password']}")
            return True
        else:
            print(f"❌ Failed to create test doctor: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test doctor: {e}")
        return False

if __name__ == '__main__':
    if create_test_doctor():
        print("✅ Test doctor creation complete")
    else:
        print("❌ Test doctor creation failed")
        sys.exit(1)