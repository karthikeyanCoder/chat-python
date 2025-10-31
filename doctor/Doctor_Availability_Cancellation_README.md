# Doctor Appointment Cancellation System - Updated Postman Collection

## 🎯 Overview
The Postman collection has been updated to include comprehensive testing for the new **Doctor Appointment Cancellation System**. This includes both individual slot cancellation and full-date cancellation features.

## 📋 New Cancellation Endpoints Added

### **❌ Doctor Appointment Cancellation Section**

#### **1. Get Booked Slots for Date**
- **Method:** `GET`
- **Endpoint:** `/doctor/{doctor_id}/availability/{date}/booked-slots`
- **Purpose:** Retrieve all booked slots for a specific date
- **Authentication:** JWT Bearer token required
- **Response:** List of booked slots with appointment details

#### **2. Cancel Individual Appointment Slot**
- **Method:** `POST`
- **Endpoint:** `/doctor/{doctor_id}/availability/{date}/{slot_id}/cancel`
- **Purpose:** Cancel a specific appointment slot and make it available
- **Authentication:** JWT Bearer token required
- **Body:**
  ```json
  {
    "appointment_id": "APT123",
    "cancellation_reason": "Patient requested reschedule"
  }
  ```

#### **3. Get Appointment Summary for Date**
- **Method:** `GET`
- **Endpoint:** `/doctor/{doctor_id}/availability/{date}/summary`
- **Purpose:** Get appointment summary by type for a specific date
- **Authentication:** JWT Bearer token required
- **Response:** Summary with booked/available counts by appointment type

#### **4. Cancel All Appointments for Date**
- **Method:** `POST`
- **Endpoint:** `/doctor/{doctor_id}/availability/{date}/cancel-all`
- **Purpose:** Cancel all appointments for a specific date
- **Authentication:** JWT Bearer token required
- **Body:**
  ```json
  {
    "cancellation_reason": "Emergency - Doctor unavailable for the day"
  }
  ```

#### **5. Test Cancel Invalid Slot**
- **Method:** `POST`
- **Endpoint:** `/doctor/{doctor_id}/availability/{date}/INVALID_SLOT/cancel`
- **Purpose:** Test error handling for non-existent slots
- **Expected:** 400 Bad Request error

#### **6. Test Cancel All - No Appointments**
- **Method:** `POST`
- **Endpoint:** `/doctor/{doctor_id}/availability/2023-01-01/cancel-all`
- **Purpose:** Test cancellation when no appointments exist
- **Expected:** Success with 0 cancelled count

#### **7. Test Unauthorized Cancellation**
- **Method:** `POST`
- **Endpoint:** `/doctor/{doctor_id}/availability/{date}/{slot_id}/cancel`
- **Purpose:** Test JWT authentication
- **Expected:** 401 Unauthorized error

## 🔧 Collection Variables Added

### **New Variables:**
- `slot_id`: `SLOT_CONSULTATION_003` - Sample slot ID for testing
- `appointment_id`: `APT123` - Sample appointment ID for testing

### **Existing Variables:**
- `base_url`: `http://localhost:5000` - API base URL
- `doctor_id`: `DOC123` - Sample doctor ID
- `test_date`: `2025-10-26` - Test date for availability
- `jwt_token`: JWT token from doctor login
- `availability_id`: `AVAIL_123456789` - Sample availability ID

## 🚀 How to Use the Updated Collection

### **Step 1: Import Collection**
1. Open Postman
2. Click "Import" button
3. Select `Doctor_Availability_Postman_Collection.json`
4. Collection will be imported with all cancellation endpoints

### **Step 2: Set Up Environment**
1. Create a new environment or use existing one
2. Set the following variables:
   - `base_url`: Your server URL (e.g., `http://localhost:5000`)
   - `doctor_id`: Your test doctor ID
   - `test_date`: Date for testing (format: YYYY-MM-DD)

### **Step 3: Authenticate**
1. Run "Doctor Login" request from Authentication section
2. Copy the JWT token from response
3. Update `jwt_token` variable in environment

### **Step 4: Test Cancellation System**

#### **Individual Slot Cancellation Flow:**
1. **Get Booked Slots** → See which slots are booked
2. **Cancel Individual Slot** → Cancel specific appointment
3. **Verify** → Check that slot is now available

#### **Full-Date Cancellation Flow:**
1. **Get Appointment Summary** → See appointment overview
2. **Cancel All Appointments** → Cancel all appointments for date
3. **Verify** → Check that all slots are now available

#### **Error Testing:**
1. **Test Cancel Invalid Slot** → Verify error handling
2. **Test Unauthorized Access** → Verify JWT protection
3. **Test No Appointments** → Verify edge case handling

## 📊 Expected Responses

### **Successful Individual Cancellation:**
```json
{
  "success": true,
  "message": "Appointment slot cancelled successfully",
  "slot_id": "SLOT_CONSULTATION_003",
  "appointment_id": "APT123"
}
```

### **Successful Full-Date Cancellation:**
```json
{
  "success": true,
  "message": "All appointments cancelled for 2025-10-26",
  "cancelled_count": 3,
  "cancelled_appointments": [
    {
      "slot_id": "SLOT_CONSULTATION_003",
      "appointment_id": "APT123",
      "patient_id": "PAT123",
      "appointment_type": "consultation",
      "start_time": "10:00",
      "end_time": "10:30"
    }
  ],
  "date": "2025-10-26",
  "doctor_id": "DOC123",
  "cancellation_reason": "Emergency - Doctor unavailable for the day"
}
```

### **Booked Slots Response:**
```json
{
  "success": true,
  "booked_slots": [
    {
      "availability_id": "AVAIL_123456789",
      "doctor_id": "DOC123",
      "date": "2025-10-26",
      "consultation_type": "in_person",
      "appointment_type": "consultation",
      "slot_id": "SLOT_CONSULTATION_003",
      "start_time": "10:00",
      "end_time": "10:30",
      "patient_id": "PAT123",
      "appointment_id": "APT123",
      "booking_timestamp": "2025-10-24T10:00:00Z",
      "notes": "Test appointment"
    }
  ],
  "total_booked": 1,
  "doctor_id": "DOC123",
  "date": "2025-10-26"
}
```

### **Appointment Summary Response:**
```json
{
  "success": true,
  "summary": {
    "success": true,
    "date": "2025-10-26",
    "doctor_id": "DOC123",
    "consultation_type": "in_person",
    "work_hours": {
      "start_time": "09:00",
      "end_time": "17:00"
    },
    "appointment_summary": {
      "consultation": {
        "booked_slots": 1,
        "available_slots": 2,
        "total_slots": 3,
        "duration_mins": 30,
        "price": 100
      },
      "follow_up": {
        "booked_slots": 1,
        "available_slots": 1,
        "total_slots": 2,
        "duration_mins": 15,
        "price": 50
      }
    },
    "totals": {
      "total_booked": 2,
      "total_available": 3,
      "total_slots": 5
    },
    "availability_id": "AVAIL_123456789"
  }
}
```

## 🔒 Security Features

### **JWT Authentication:**
- All cancellation endpoints require valid JWT token
- Token must match the doctor_id in the URL
- Invalid tokens return 401 Unauthorized

### **Input Validation:**
- Date format validation (YYYY-MM-DD)
- Required field validation
- Appointment ID validation
- Slot ID validation

### **Error Handling:**
- Comprehensive error messages
- Proper HTTP status codes
- Database error handling
- Graceful failure responses

## 🧪 Testing Scenarios Covered

### **Happy Path Tests:**
- ✅ Individual slot cancellation
- ✅ Full-date cancellation
- ✅ Booked slots retrieval
- ✅ Appointment summary

### **Error Scenarios:**
- ✅ Invalid slot ID
- ✅ Invalid appointment ID
- ✅ Non-existent date
- ✅ Unauthorized access
- ✅ Missing required fields

### **Edge Cases:**
- ✅ No appointments to cancel
- ✅ Already cancelled slots
- ✅ Invalid date format
- ✅ Database connection errors

## 📈 Benefits of Updated Collection

1. **Complete Coverage:** Tests all cancellation functionality
2. **Real-world Scenarios:** Includes practical use cases
3. **Error Testing:** Comprehensive error scenario coverage
4. **Easy Setup:** Pre-configured with sample data
5. **Documentation:** Clear descriptions for each endpoint
6. **Variables:** Reusable variables for easy customization

## 🎯 Next Steps

1. **Import Collection:** Load the updated collection into Postman
2. **Configure Environment:** Set up your environment variables
3. **Run Tests:** Execute the cancellation endpoints
4. **Verify Results:** Check that cancellations work as expected
5. **Customize:** Modify variables for your specific use case

The updated Postman collection provides comprehensive testing for the new Doctor Appointment Cancellation System, ensuring all functionality works correctly and handles errors gracefully! 🚀
