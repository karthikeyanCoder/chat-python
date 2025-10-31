#!/usr/bin/env python3
"""
Complete Doctor Availability System Test Script
Tests all components: Database, Model, Controller, and API endpoints
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_availability_system():
    """Test the complete availability system"""
    print("🧪 Testing Complete Doctor Availability System")
    print("=" * 60)
    
    # Test configuration
    BASE_URL = "http://localhost:5000"
    TEST_DOCTOR_ID = "DOC123"
    TEST_DATE = "2025-10-26"
    
    # Test data using your model structure
    test_availability_data = {
        "date": TEST_DATE,
        "work_hours": {
            "start_time": "09:00",
            "end_time": "17:00"
        },
        "consultation_type": "Online",
        "types": [
            {
                "type": "Consultation",
                "duration_mins": 30,
                "price": 150.0,
                "currency": "USD",
                "slots": [
                    { "start_time": "09:00", "end_time": "09:30", "is_booked": False },
                    { "start_time": "09:30", "end_time": "10:00", "is_booked": False },
                    { "start_time": "10:00", "end_time": "10:30", "is_booked": True, "patient_id": "PAT123", "appointment_id": "APT123" }
                ]
            },
            {
                "type": "Follow-up",
                "duration_mins": 20,
                "price": 100.0,
                "currency": "USD",
                "slots": [
                    { "start_time": "11:00", "end_time": "11:20", "is_booked": False },
                    { "start_time": "11:20", "end_time": "11:40", "is_booked": False }
                ]
            },
            {
                "type": "First Visit",
                "duration_mins": 45,
                "price": 200.0,
                "currency": "USD",
                "slots": [
                    { "start_time": "14:00", "end_time": "14:45", "is_booked": False },
                    { "start_time": "15:00", "end_time": "15:45", "is_booked": True, "patient_id": "PAT456", "appointment_id": "APT456" }
                ]
            },
            {
                "type": "Report Review",
                "duration_mins": 15,
                "price": 75.0,
                "currency": "USD",
                "slots": [
                    { "start_time": "16:00", "end_time": "16:15", "is_booked": False },
                    { "start_time": "16:15", "end_time": "16:30", "is_booked": False }
                ]
            }
        ],
        "breaks": [
            {
                "start_time": "12:00",
                "end_time": "13:00",
                "type": "lunch",
                "is_blocked": True
            }
        ]
    }
    
    # Mock JWT token for testing (in real scenario, this would come from login)
    mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkb2N0b3JfaWQiOiJET0MxMjMiLCJleHAiOjE3MzI1NjQ4MDB9.test_signature"
    
    headers = {
        "Authorization": f"Bearer {mock_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Create Availability
        print("\n🧪 Test 1: Creating Doctor Availability...")
        create_url = f"{BASE_URL}/doctor/{TEST_DOCTOR_ID}/availability"
        
        try:
            response = requests.post(create_url, json=test_availability_data, headers=headers, timeout=10)
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Availability created successfully")
                print(f"   - Availability ID: {result.get('availability_id')}")
                availability_id = result.get('availability_id')
            else:
                print(f"❌ Creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - Is the server running?")
            print("   Start the server with: python app_mvc.py")
            return False
        
        # Test 2: Get Availability by Date
        print("\n🧪 Test 2: Getting Availability by Date...")
        get_url = f"{BASE_URL}/doctor/{TEST_DOCTOR_ID}/availability/{TEST_DATE}"
        
        response = requests.get(get_url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Availability retrieved successfully")
            print(f"   - Total availability records: {result.get('total_count', 0)}")
            if result.get('availability'):
                avail_doc = result['availability'][0]
                print(f"   - Doctor ID: {avail_doc.get('doctor_id')}")
                print(f"   - Date: {avail_doc.get('date')}")
                print(f"   - Consultation Type: {avail_doc.get('consultation_type')}")
                print(f"   - Total appointment types: {len(avail_doc.get('types', []))}")
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 3: Get Available Slots by Type
        print("\n🧪 Test 3: Getting Available Slots by Type...")
        slots_url = f"{BASE_URL}/doctor/{TEST_DOCTOR_ID}/availability/{TEST_DATE}/Consultation"
        
        response = requests.get(slots_url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Available Consultation slots retrieved")
            print(f"   - Total available slots: {result.get('total_available', 0)}")
            print(f"   - Doctor ID: {result.get('doctor_id')}")
            print(f"   - Date: {result.get('date')}")
            print(f"   - Appointment Type: {result.get('appointment_type')}")
            
            if result.get('slots'):
                print("   - Available slots:")
                for slot in result['slots']:
                    print(f"     * {slot['start_time']} to {slot['end_time']} (${slot.get('price', 0)})")
        else:
            print(f"❌ Slot retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 4: Test Public Endpoints (for patients)
        print("\n🧪 Test 4: Testing Public Endpoints...")
        public_url = f"{BASE_URL}/public/doctor/{TEST_DOCTOR_ID}/availability/{TEST_DATE}"
        
        response = requests.get(public_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Public availability endpoint working")
            print(f"   - Total availability records: {result.get('total_count', 0)}")
        else:
            print(f"❌ Public endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 5: Update Availability
        print("\n🧪 Test 5: Updating Availability...")
        update_data = {
            "consultation_type": "In-Person",
            "work_hours": {
                "start_time": "08:00",
                "end_time": "18:00"
            }
        }
        
        update_url = f"{BASE_URL}/availability/{availability_id}"
        response = requests.put(update_url, json=update_data, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Availability updated successfully")
            print(f"   - Message: {result.get('message')}")
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 6: Delete Availability
        print("\n🧪 Test 6: Deleting Availability...")
        delete_url = f"{BASE_URL}/availability/{availability_id}"
        response = requests.delete(delete_url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Availability deleted successfully")
            print(f"   - Message: {result.get('message')}")
        else:
            print(f"❌ Deletion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        print("\n✅ All API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_directly():
    """Test the model directly without API"""
    print("\n🧪 Testing Model Directly...")
    try:
        from models.database import Database
        from models.doctor_availability_model import DoctorAvailabilityModel
        
        # Initialize database
        db = Database()
        if not db.connect():
            print("❌ Database connection failed")
            return False
        
        print("✅ Database connected successfully")
        
        # Initialize model
        availability_model = DoctorAvailabilityModel(db)
        print("✅ Availability model initialized")
        
        # Test data
        test_data = {
            "date": "2025-10-27",
            "work_hours": {
                "start_time": "09:00",
                "end_time": "17:00"
            },
            "consultation_type": "Online",
            "types": [
                {
                    "type": "Consultation",
                    "duration_mins": 30,
                    "price": 150.0,
                    "currency": "USD",
                    "slots": [
                        { "start_time": "09:00", "end_time": "09:30", "is_booked": False },
                        { "start_time": "09:30", "end_time": "10:00", "is_booked": False }
                    ]
                }
            ]
        }
        
        # Test model operations
        print("🧪 Testing model operations...")
        
        # Create availability
        result = availability_model.create_daily_availability("DOC456", "2025-10-27", test_data)
        if result['success']:
            print(f"✅ Model: Availability created - {result['availability_id']}")
            availability_id = result['availability_id']
        else:
            print(f"❌ Model: Creation failed - {result['error']}")
            return False
        
        # Get availability
        result = availability_model.get_doctor_availability("DOC456", "2025-10-27")
        if result['success']:
            print(f"✅ Model: Availability retrieved - {result['total_count']} records")
        else:
            print(f"❌ Model: Retrieval failed - {result['error']}")
            return False
        
        # Clean up
        result = availability_model.delete_availability(availability_id)
        if result['success']:
            print("✅ Model: Test data cleaned up")
        else:
            print(f"⚠️ Model: Cleanup warning - {result['error']}")
        
        print("✅ Model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Doctor Availability System Tests")
    print("=" * 60)
    
    # Test model directly first
    model_success = test_model_directly()
    
    # Test API endpoints
    api_success = test_complete_availability_system()
    
    if model_success and api_success:
        print("\n🎉 All tests completed successfully!")
        print("✅ Doctor Availability System is ready!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        if not model_success:
            print("❌ Model tests failed")
        if not api_success:
            print("❌ API tests failed")
        sys.exit(1)
