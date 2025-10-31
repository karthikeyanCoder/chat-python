# Doctor Availability System - Postman Collection

## 📋 Overview

This Postman collection provides comprehensive testing for the Doctor Availability System. The system allows doctors to create availability slots, manage appointments, and cancel bookings. Patients can view available slots through public endpoints.

## 🚀 Quick Start

### 1. Import Collection and Environment

**Import Collection:**
- Open Postman
- Click "Import" button
- Select `Doctor_Availability_Postman_Collection.json`
- The collection will be imported with all endpoints organized in folders

**Import Environment:**
- Click "Import" button
- Select `Doctor_Availability_Environment.json`
- Click on the environment dropdown (top right)
- Select "Doctor Availability Environment"

### 2. Configure Environment Variables

Update these variables in the environment:
- `base_url`: Your server URL (default: `http://localhost:5000`)
- `doctor_id`: Your doctor ID (get this after login)
- `doctor_email`: Your doctor email for login
- `doctor_password`: Your doctor password

### 3. Start the Server

```bash
cd doctor
python app_mvc.py
# OR
python app_clinic.py
```

The server should run on `http://localhost:5000`

## 📁 Collection Structure

### 🔐 Authentication
- **Doctor Login**: Login to get JWT token
  - Endpoint: `POST /doctor-login`
  - After login, copy the `access_token` from response and update `jwt_token` in environment

### 👨‍⚕️ Doctor Availability Management (Protected Routes)

All endpoints require JWT authentication (Bearer token):

1. **Create Daily Availability**
   - `POST /doctor/{doctor_id}/availability`
   - Create availability slots for a specific date
   - Supports multiple appointment types (Consultation, Follow-up, First Visit, Report Review)
   - Includes work hours, breaks, and slot details

2. **Get All Doctor Availability**
   - `GET /doctor/{doctor_id}/availability`
   - Get all availability records for a doctor
   - Optional query params: `date`, `start_date`, `end_date`

3. **Get Availability by Date**
   - `GET /doctor/{doctor_id}/availability/{date}`
   - Get availability for a specific date
   - Date format: `YYYY-MM-DD`

4. **Get Available Slots by Type**
   - `GET /doctor/{doctor_id}/availability/{date}/{type}`
   - Get available slots for specific appointment type
   - Types: `Consultation`, `Follow-up`, `First Visit`, `Report Review`

5. **Update Availability**
   - `PUT /availability/{availability_id}`
   - Update existing availability document

6. **Delete Availability**
   - `DELETE /availability/{availability_id}`
   - Soft delete availability document

### 🌐 Public Availability (Patient View)

No authentication required - these endpoints are for patients:

1. **Public - Get Doctor Availability**
   - `GET /public/doctor/{doctor_id}/availability/{date}`
   - View doctor availability for a specific date

2. **Public - Get Available Slots by Type**
   - `GET /public/doctor/{doctor_id}/availability/{date}/{type}`
   - View available slots for specific appointment type

3. **Public - Get Follow-up Slots**
   - `GET /public/doctor/{doctor_id}/availability/{date}/Follow-up`

4. **Public - Get First Visit Slots**
   - `GET /public/doctor/{doctor_id}/availability/{date}/First Visit`

5. **Public - Get Report Review Slots**
   - `GET /public/doctor/{doctor_id}/availability/{date}/Report Review`

### ❌ Doctor Appointment Cancellation

1. **Get Booked Slots for Date**
   - `GET /doctor/{doctor_id}/availability/{date}/booked-slots`
   - View all booked slots for a specific date

2. **Cancel Individual Appointment Slot**
   - `POST /doctor/{doctor_id}/availability/{date}/{slot_id}/cancel`
   - Cancel a specific appointment slot
   - Body: `{ "appointment_id": "...", "cancellation_reason": "..." }`

3. **Get Appointment Summary for Date**
   - `GET /doctor/{doctor_id}/availability/{date}/summary`
   - Get appointment summary by type (booked/available counts)

4. **Cancel All Appointments for Date**
   - `POST /doctor/{doctor_id}/availability/{date}/cancel-all`
   - Cancel all appointments for a specific date
   - Body: `{ "cancellation_reason": "..." }`

### 🧪 Test Scenarios

Test cases for error handling:
1. Invalid date format
2. Missing required fields
3. Invalid time format
4. Unauthorized access
5. Invalid doctor ID

### 📊 Sample Responses

Reference examples showing expected response formats

## 🎯 Testing Workflow

### Step 1: Authentication
1. Run "Doctor Login" request
2. Copy the `access_token` from response
3. Update `jwt_token` variable in environment (click eye icon → Edit)

### Step 2: Create Availability
1. Update `test_date` variable (format: `YYYY-MM-DD`)
2. Update `doctor_id` variable with your doctor ID
3. Run "1. Create Daily Availability"
4. Copy the `availability_id` from response
5. Update `availability_id` variable

### Step 3: View Availability
1. Run "2. Get All Doctor Availability" to see all records
2. Run "3. Get Availability by Date" for specific date
3. Run "4. Get Available Slots by Type" for specific type

### Step 4: Test Public Endpoints
1. Run "Public - Get Doctor Availability" (no auth needed)
2. Test other public endpoints

### Step 5: Test Cancellation
1. Run "Get Booked Slots for Date" to see booked slots
2. Run "Cancel Individual Appointment Slot" with valid slot_id
3. Run "Get Appointment Summary" to see overview
4. Run "Cancel All Appointments" if needed

### Step 6: Test Error Scenarios
1. Run all "Test Scenarios" to verify error handling

## 📝 Request Examples

### Create Availability Request Body

```json
{
  "date": "2025-01-30",
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
        { "start_time": "09:00", "end_time": "09:30", "is_booked": false },
        { "start_time": "09:30", "end_time": "10:00", "is_booked": false }
      ]
    },
    {
      "type": "Follow-up",
      "duration_mins": 20,
      "price": 100.0,
      "currency": "USD",
      "slots": [
        { "start_time": "11:00", "end_time": "11:20", "is_booked": false }
      ]
    }
  ],
  "breaks": [
    {
      "start_time": "12:00",
      "end_time": "13:00",
      "type": "lunch",
      "is_blocked": true
    }
  ]
}
```

### Cancel Appointment Request Body

```json
{
  "appointment_id": "APT123",
  "cancellation_reason": "Patient requested reschedule"
}
```

## 🔧 Troubleshooting

### Common Issues

1. **401 Unauthorized Error**
   - Verify JWT token is valid and not expired
   - Check if token matches the doctor_id in URL
   - Re-login and update `jwt_token` variable

2. **400 Bad Request Error**
   - Verify JSON format matches expected structure
   - Check required fields are present
   - Validate date format: `YYYY-MM-DD`
   - Validate time format: `HH:MM` (24-hour format)

3. **Connection Error**
   - Ensure server is running on the correct port
   - Check `base_url` variable matches server URL
   - Verify network connectivity

4. **404 Not Found**
   - Verify doctor_id exists
   - Check availability_id is valid
   - Ensure date format is correct

### Environment Variables Checklist

✅ `base_url`: Server URL (e.g., `http://localhost:5000`)  
✅ `jwt_token`: JWT token from doctor login  
✅ `doctor_id`: Your doctor ID  
✅ `test_date`: Date for testing (format: `YYYY-MM-DD`)  
✅ `availability_id`: Availability ID from create response  
✅ `slot_id`: Slot ID for cancellation testing  
✅ `appointment_id`: Appointment ID for cancellation  

## 📊 Expected Status Codes

- **200 OK**: Successful GET requests
- **201 Created**: Successful POST requests
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server/database error

## 🎯 Features

- ✅ Complete CRUD operations for availability
- ✅ Multiple appointment types support
- ✅ Public endpoints for patient view
- ✅ Appointment cancellation (individual and bulk)
- ✅ Comprehensive error testing
- ✅ Sample responses for reference
- ✅ Environment variables for easy configuration

## 📞 Additional Resources

- Main README: `doctor/Doctor_Availability_Postman_README.md`
- Cancellation Guide: `doctor/Doctor_Availability_Cancellation_README.md`
- API Documentation: Check `doctor/API_QUICK_REFERENCE.md`

---

**Happy Testing! 🚀**

