#!/usr/bin/env python3
"""
Quick Test for JWT Token Fix
Tests if the JWT token now includes the 'type: access_token' field
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Configuration
PATIENT_MODULE_URL = "http://localhost:5002"  # Patient module
DOCTOR_MODULE_URL = "http://localhost:5000"   # Doctor module

def test_jwt_token_fix():
    """Test if JWT token fix resolves the authentication issue"""
    print("🔧 Testing JWT Token Fix...")
    
    # Step 1: Patient Login
    print("\n1️⃣ Testing Patient Login...")
    login_data = {
        "login_identifier": "deepikim24@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{PATIENT_MODULE_URL}/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            patient_id = data.get('patient_id')
            
            print(f"✅ Login successful!")
            print(f"Patient ID: {patient_id}")
            print(f"Token: {token[:50]}...")
            
            # Step 2: Test Doctor Availability
            print("\n2️⃣ Testing Doctor Availability with Fixed Token...")
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{PATIENT_MODULE_URL}/patient/doctor/DOC123/availability/2025-01-26"
            print(f"URL: {url}")
            
            response = requests.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! JWT token fix worked!")
                print("✅ Doctor availability retrieved successfully!")
                return True
            else:
                print(f"❌ Still getting error: {response.text}")
                return False
                
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 JWT Token Fix Test")
    print("=" * 40)
    
    success = test_jwt_token_fix()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 JWT Token Fix SUCCESSFUL!")
        print("✅ Patient can now access doctor availability")
    else:
        print("❌ JWT Token Fix FAILED!")
        print("🔧 Check the implementation")
    print("=" * 40)

if __name__ == "__main__":
    main()
