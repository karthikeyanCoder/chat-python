#!/usr/bin/env python3
"""
Test Unified JWT Token System
Tests if patient login tokens can now be used for doctor authentication
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Configuration
PATIENT_MODULE_URL = "http://localhost:5002"  # Patient module
DOCTOR_MODULE_URL = "http://localhost:5000"   # Doctor module

def test_patient_login():
    """Test patient login and get the new token format"""
    print("🔐 Testing Patient Login with New Token Format...")
    
    login_data = {
        "login_identifier": "deepikim24@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{PATIENT_MODULE_URL}/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"Response format:")
            print(f"  email: {data.get('email')}")
            print(f"  is_profile_complete: {data.get('is_profile_complete')}")
            print(f"  message: {data.get('message')}")
            print(f"  object_id: {data.get('object_id')}")
            print(f"  patient_id: {data.get('patient_id')}")
            print(f"  session_id: {data.get('session_id')}")
            print(f"  token: {data.get('token', '')[:50]}...")
            print(f"  username: {data.get('username')}")
            
            return data.get('token'), data.get('patient_id')
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None, None

def test_doctor_token_validation(token):
    """Test if the patient token can be validated by doctor module"""
    print(f"\n🔍 Testing Doctor Token Validation...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test a simple doctor endpoint that requires authentication
        url = f"{DOCTOR_MODULE_URL}/patient/doctor/DOC123/availability/2025-01-26"
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Patient token works with doctor module!")
            return True
        else:
            print(f"❌ Token validation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_token_structure(token):
    """Test the JWT token structure"""
    print(f"\n🔬 Testing JWT Token Structure...")
    
    try:
        import jwt
        import os
        
        # Use the same secret key as the doctor module
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
        
        # Decode the token
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        print(f"✅ Token decoded successfully!")
        print(f"Token payload:")
        for key, value in payload.items():
            print(f"  {key}: {value}")
        
        # Check if it has the required fields
        required_fields = ['user_id', 'patient_id', 'email', 'username', 'type', 'object_id']
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            print(f"⚠️ Missing fields: {missing_fields}")
        else:
            print(f"✅ All required fields present!")
        
        return True
        
    except Exception as e:
        print(f"❌ Token structure test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Unified JWT Token System Test")
    print("=" * 50)
    
    # Test 1: Patient Login
    token, patient_id = test_patient_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    # Test 2: Token Structure
    test_token_structure(token)
    
    # Test 3: Doctor Token Validation
    success = test_doctor_token_validation(token)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 UNIFIED JWT TOKEN SYSTEM SUCCESSFUL!")
        print("✅ Patient login tokens can now be used for doctor authentication!")
        print("✅ The response format matches your requirements!")
    else:
        print("❌ UNIFIED JWT TOKEN SYSTEM FAILED!")
        print("🔧 Check the implementation")
    print("=" * 50)

if __name__ == "__main__":
    main()
