#!/usr/bin/env python3
"""
Test Complete Slot Booking Flow
Tests the enhanced appointment booking with slot validation and booking
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Configuration
PATIENT_MODULE_URL = "http://localhost:5002"  # Patient module
DOCTOR_MODULE_URL = "http://localhost:5000"   # Doctor module

def test_complete_flow():
    """Test the complete slot booking flow"""
    print("🧪 Testing Complete Slot Booking Flow")
    print("=" * 60)
    
    # Step 1: Patient Login
    print("🔐 Step 1: Patient Login")
    token, patient_id = test_patient_login()
    if not token or not patient_id:
        print("❌ Cannot proceed without valid login")
        return False
    
    # Step 2: Get Available Slots
    print("\n📅 Step 2: Get Available Slots")
    slots_before = test_get_available_slots()
    if not slots_before:
        print("❌ No slots available for testing")
        return False
    
    # Step 3: Book Appointment with Slot ID
    print("\n📝 Step 3: Book Appointment with Slot ID")
    booking_success = test_enhanced_appointment_booking(token, patient_id, slots_before[0])
    if not booking_success:
        print("❌ Appointment booking failed")
        return False
    
    # Step 4: Verify Slot is Booked (Get Available Slots Again)
    print("\n🔍 Step 4: Verify Slot is Booked")
    slots_after = test_get_available_slots()
    if slots_after:
        # Check if the booked slot is no longer available
        booked_slot_id = slots_before[0]['slot_id']
        still_available = any(slot['slot_id'] == booked_slot_id for slot in slots_after)
        
        if still_available:
            print(f"❌ Slot {booked_slot_id} is still available - booking failed!")
            return False
        else:
            print(f"✅ Slot {booked_slot_id} is no longer available - booking successful!")
    else:
        print("⚠️ No slots available after booking (all slots might be booked)")
    
    print("\n🎉 Complete flow test completed successfully!")
    return True

def test_patient_login():
    """Test patient login to get JWT token"""
    login_data = {
        "login_identifier": "deepikim24@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{PATIENT_MODULE_URL}/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            patient_id = data.get('patient_id')
            
            print(f"✅ Login successful! Patient ID: {patient_id}")
            return token, patient_id
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None, None

def test_get_available_slots(doctor_id="D17597662805576911", appointment_type="Consultation"):
    """Test getting available slots from doctor availability system"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        url = f"{DOCTOR_MODULE_URL}/public/doctor/{doctor_id}/availability/{tomorrow}/{appointment_type}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('available_slots'):
                slots = data['available_slots']
                print(f"✅ Found {len(slots)} available slots")
                
                for i, slot in enumerate(slots[:3]):  # Show first 3 slots
                    print(f"  {i+1}. Slot ID: {slot.get('slot_id')}")
                    print(f"     Time: {slot.get('start_time')} - {slot.get('end_time')}")
                    print(f"     Price: {slot.get('price')} {slot.get('currency')}")
                
                return slots
            else:
                print("No slots available")
                return None
        else:
            print(f"❌ Failed to get slots: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting slots: {str(e)}")
        return None

def test_enhanced_appointment_booking(token, patient_id, slot_data):
    """Test enhanced appointment booking with slot_id"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    appointment_data = {
        "slot_id": slot_data["slot_id"],
        "appointment_date": tomorrow,
        "appointment_time": slot_data["start_time"],
        "type": "Consultation",
        "appointment_type": "Consultation",
        "notes": "Complete flow test",
        "patient_notes": "Testing slot booking integration",
        "doctor_id": "D17597662805576911"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{PATIENT_MODULE_URL}/patient/appointments",
            json=appointment_data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Appointment booking successful!")
            print(f"Appointment ID: {data.get('appointment_id')}")
            print(f"Slot ID: {data.get('slot_id')}")
            print(f"Slot Time: {data.get('slot_start_time')} - {data.get('slot_end_time')}")
            return True
        else:
            print(f"❌ Appointment booking failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Booking error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 All tests passed! Slot booking flow is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
