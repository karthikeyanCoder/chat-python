# 🏥 Patient Appointments with Availability - Postman Collection

## 📋 Overview

This Postman collection provides comprehensive testing for patient appointment management with doctor availability slots. It includes authentication, doctor discovery, availability checking, appointment booking, and management workflows.

## 🚀 Quick Start

### 1. Import Collection
- Import `Patient_Appointments_with_Availability.postman_collection.json` into Postman
- Set up environment variables (see Environment Setup below)

### 2. Environment Setup
Create a new environment with these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:5002` | Patient app base URL |
| `auth_token` | (auto-set) | JWT token from login |
| `patient_id` | (auto-set) | Patient ID from login |
| `doctor_id` | `D17597286260221902` | Doctor ID for testing |
| `appointment_date` | (auto-set) | Tomorrow's date |
| `appointment_type` | `consultation` | Appointment type |
| `slot_id` | (auto-set) | Available slot ID |
| `appointment_id` | (auto-set) | Created appointment ID |

### 3. Authentication Flow
1. **Login**: Run "1. Patient Login" to get JWT token
2. **Token**: Automatically saved to `auth_token` variable
3. **Use**: All subsequent requests use the token

## 📚 Collection Structure

### 🔐 Authentication
- **Patient Login**: Login with email/patient_id and password
- **Patient Logout**: Logout and invalidate token

### 👨‍⚕️ Doctor Discovery
- **Get All Doctors**: List all available doctors with filters
- **Get Doctor Profile**: Get detailed doctor information

### 📅 Doctor Availability
- **Get Doctor Availability**: Get availability for specific date
- **Get Available Slots by Type**: Get slots filtered by appointment type
- **Get Availability Slots (Enhanced)**: Enhanced slots with detailed info

### 📋 Appointment Management
- **Get Patient Appointments**: List all patient appointments
- **Create Appointment (with Slot)**: Book appointment with specific slot
- **Create Video Call Appointment**: Book video call appointment
- **Get Specific Appointment**: Get appointment details
- **Update Appointment**: Modify appointment details
- **Cancel Appointment**: Cancel/delete appointment

### 📊 Appointment Analytics
- **Get Upcoming Appointments**: List upcoming appointments
- **Get Appointment History**: List past appointments
- **Get Appointment Statistics**: Get appointment analytics

### 🔍 Slot Validation
- **Validate Slot Availability**: Check if slot is still available

## 🔧 Request Examples

### Login Request
```json
POST /auth/login
{
  "login_identifier": "patient@example.com",
  "password": "password123"
}
```

### Get Doctor Availability
```http
GET /doctors/doctor/D17597286260221902/availability/2024-01-30
Authorization: Bearer {{auth_token}}
```

### Create Appointment
```json
POST /appointments/patient/appointments
{
  "appointment_date": "2024-01-30",
  "appointment_time": "10:00",
  "type": "consultation",
  "appointment_type": "in-person",
  "slot_id": "slot_001",
  "notes": "Regular checkup appointment",
  "patient_notes": "Feeling good, no urgent concerns",
  "doctor_id": "D17597286260221902"
}
```

### Get Available Slots
```http
GET /doctors/doctor/D17597286260221902/availability/2024-01-30/consultation
Authorization: Bearer {{auth_token}}
```

## 📊 Response Examples

### Login Response
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpV...",
  "patient_id": "PAT1234567890ABCDEF",
  "email": "patient@example.com",
  "username": "johndoe",
  "is_profile_complete": true
}
```

### Availability Response
```json
{
  "success": true,
  "doctor_id": "D17597286260221902",
  "date": "2024-01-30",
  "appointment_type": "consultation",
  "total_slots": 8,
  "available_slots": 6,
  "slots": [
    {
      "slot_id": "slot_001",
      "start_time": "09:00",
      "end_time": "09:30",
      "appointment_type": "consultation",
      "status": "available",
      "duration_minutes": 30,
      "price": 150.0
    }
  ]
}
```

### Appointment Created Response
```json
{
  "success": true,
  "message": "Appointment created successfully",
  "appointment_id": "APT1758712159E182A4",
  "appointment": {
    "appointment_id": "APT1758712159E182A4",
    "patient_id": "PAT1234567890ABCDEF",
    "doctor_id": "D17597286260221902",
    "appointment_date": "2024-01-30",
    "appointment_time": "10:00",
    "appointment_type": "in-person",
    "status": "scheduled",
    "notes": "Regular checkup appointment"
  }
}
```

## 🔄 Workflow Examples

### Complete Appointment Booking Flow

1. **Login Patient**
   ```
   POST /auth/login
   → Save token to environment
   ```

2. **Get Available Doctors**
   ```
   GET /doctors/doctors
   → Select doctor_id
   ```

3. **Check Doctor Availability**
   ```
   GET /doctors/doctor/{doctor_id}/availability/{date}
   → Review available slots
   ```

4. **Get Specific Slots**
   ```
   GET /doctors/doctor/{doctor_id}/availability/{date}/{type}
   → Select slot_id
   ```

5. **Create Appointment**
   ```
   POST /appointments/patient/appointments
   → Book appointment with slot
   ```

6. **Verify Appointment**
   ```
   GET /appointments/patient/appointments/{appointment_id}
   → Confirm booking
   ```

### Video Call Appointment Flow

1. **Get Video Call Slots**
   ```
   GET /doctors/doctor/{doctor_id}/availability/{date}/consultation
   → Filter for video-call compatible slots
   ```

2. **Create Video Call Appointment**
   ```
   POST /appointments/patient/appointments
   {
     "appointment_type": "video-call",
     "video_link": "https://meet.google.com/abc-defg-hij"
   }
   ```

## 🎯 Testing Scenarios

### Happy Path Testing
1. Login → Get Doctors → Check Availability → Book Appointment → Verify
2. Login → Get Appointments → Update Appointment → Cancel Appointment

### Error Handling Testing
1. **Invalid Credentials**: Test with wrong password
2. **Expired Token**: Test with expired JWT token
3. **Slot Already Booked**: Test booking unavailable slot
4. **Invalid Date**: Test with past date
5. **Missing Required Fields**: Test incomplete requests

### Edge Cases Testing
1. **No Available Slots**: Test when doctor has no availability
2. **Same Day Booking**: Test booking for today
3. **Multiple Appointments**: Test booking multiple appointments
4. **Slot Validation**: Test slot availability changes

## 🔍 Query Parameters

### Doctor Search Filters
```
GET /doctors/doctors?specialty=cardiology&location=mumbai&limit=20&offset=0
```

### Appointment Filters
```
GET /appointments/patient/appointments?date=2024-01-30&status=scheduled&type=consultation
```

### Availability Filters
```
GET /doctors/doctor/{doctor_id}/slots/{date}?appointment_type=consultation
```

## 📝 Appointment Types

| Type | Description | Duration |
|------|-------------|----------|
| `consultation` | General consultation | 30 min |
| `follow-up` | Follow-up visit | 20 min |
| `first-visit` | First time visit | 45 min |
| `report-review` | Report review | 15 min |
| `emergency` | Emergency consultation | 60 min |

## 🎨 Appointment Modes

| Mode | Description | Requirements |
|------|-------------|--------------|
| `in-person` | Physical visit | Clinic address |
| `video-call` | Online consultation | Video link |

## ⚠️ Important Notes

### Authentication
- All endpoints (except login) require JWT token
- Token expires after 24 hours
- Include `Authorization: Bearer {token}` header

### Slot Booking
- Slots are first-come-first-served
- Validate slot availability before booking
- Slots can be booked up to 30 days in advance

### Error Handling
- Check response status codes
- Review error messages in response body
- Common errors: 401 (Unauthorized), 404 (Not Found), 400 (Bad Request)

### Environment Variables
- Variables are automatically set by test scripts
- Update `base_url` for different environments
- `doctor_id` can be changed for different doctors

## 🚀 Advanced Features

### Automated Testing
- Test scripts automatically save IDs to environment
- Response validation and logging
- Error detection and reporting

### Dynamic Data
- Tomorrow's date automatically set
- Slot IDs captured from availability responses
- Appointment IDs saved for updates/cancellations

### Workflow Automation
- Complete booking flow in sequence
- Automatic token management
- Environment variable synchronization

## 📞 Support

For issues or questions:
1. Check the response logs in Postman console
2. Verify environment variables are set correctly
3. Ensure patient app is running on correct port
4. Check doctor module connectivity

## 🔄 Updates

This collection is regularly updated to match the latest API changes. Check for updates in the repository.

---

**Happy Testing! 🎉**
