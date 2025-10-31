#!/usr/bin/env python3
"""
Test Patient Doctor Availability System
Tests the complete workflow from patient login to doctor availability fetching
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Configuration
PATIENT_MODULE_URL = "http://localhost:5002"  # Patient module (run_app.py uses port 5002)
DOCTOR_MODULE_URL = "http://localhost:5000"   # Doctor module

def test_patient_login():
    """Test patient login and JWT token generation"""
    print("🔐 Testing Patient Login...")
    
    login_data = {
        "login_identifier": "deepikim24@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{PATIENT_MODULE_URL}/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            patient_id = data.get('patient_id')
            
            print(f"✅ Login successful!")
            print(f"Patient ID: {patient_id}")
            print(f"Token: {token[:50]}...")
            
            return token, patient_id
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None, None

def test_doctor_availability_via_patient_module(token, doctor_id, date):
    """Test getting doctor availability through patient module with JWT"""
    print(f"\n🏥 Testing Doctor Availability via Patient Module (JWT)...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"{PATIENT_MODULE_URL}/patient/doctor/{doctor_id}/availability/{date}"
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved doctor availability!")
            return True
        else:
            print(f"❌ Failed to get doctor availability: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_available_slots_via_patient_module(token, doctor_id, date, appointment_type):
    """Test getting available slots through patient module with JWT"""
    print(f"\n📅 Testing Available Slots via Patient Module (JWT)...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"{PATIENT_MODULE_URL}/patient/doctor/{doctor_id}/availability/{date}/{appointment_type}"
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved available slots!")
            return True
        else:
            print(f"❌ Failed to get available slots: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_direct_doctor_module_access(token, doctor_id, date):
    """Test direct access to doctor module JWT-protected endpoints"""
    print(f"\n🔒 Testing Direct Doctor Module Access (JWT)...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"{DOCTOR_MODULE_URL}/patient/doctor/{doctor_id}/availability/{date}"
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully accessed doctor module directly!")
            return True
        else:
            print(f"❌ Failed to access doctor module: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_public_doctor_module_access(doctor_id, date):
    """Test public access to doctor module (no authentication)"""
    print(f"\n🌐 Testing Public Doctor Module Access...")
    
    try:
        url = f"{DOCTOR_MODULE_URL}/public/doctor/{doctor_id}/availability/{date}"
        print(f"URL: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully accessed public endpoint!")
            return True
        else:
            print(f"❌ Failed to access public endpoint: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Patient Doctor Availability System Test")
    print("=" * 60)
    
    # Test configuration
    doctor_id = "DOC123"
    date = "2025-01-26"
    appointment_type = "consultation"
    
    print(f"Test Configuration:")
    print(f"  Patient Module: {PATIENT_MODULE_URL}")
    print(f"  Doctor Module: {DOCTOR_MODULE_URL}")
    print(f"  Doctor ID: {doctor_id}")
    print(f"  Date: {date}")
    print(f"  Appointment Type: {appointment_type}")
    print("=" * 60)
    
    # Test 1: Patient Login
    token, patient_id = test_patient_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    # Test 2: Public Doctor Module Access (should work)
    test_public_doctor_module_access(doctor_id, date)
    
    # Test 3: Direct Doctor Module Access (JWT-protected)
    test_direct_doctor_module_access(token, doctor_id, date)
    
    # Test 4: Patient Module → Doctor Module (JWT-protected)
    test_doctor_availability_via_patient_module(token, doctor_id, date)
    
    # Test 5: Available Slots via Patient Module
    test_available_slots_via_patient_module(token, doctor_id, date, appointment_type)
    
    print("\n" + "=" * 60)
    print("🎯 Patient Doctor Availability System Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
