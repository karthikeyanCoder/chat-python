# Complete API Documentation

## 📋 Overview

Complete Postman collection for the Patient Alert System API including Authentication, Doctor Management, Appointments CRUD, and Patient Selection.

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click **"Import"** → **"Upload Files"**
3. Select `Complete_API_Postman_Collection.json`
4. Click **"Import"**

### 2. Environment Variables
The collection uses these variables (auto-populated from responses):
- `base_url`: `http://localhost:8000`
- `signup_token`: JWT token from signup
- `access_token`: JWT access token
- `refresh_token`: JWT refresh token
- `reset_token`: JWT token for password reset
- `doctor_id`: Doctor identifier
- `patient_id`: Patient identifier
- `appointment_id`: Appointment identifier

---

## 📁 Collection Structure

### 1️⃣ Authentication
- **Doctor Signup** - Register new doctor
- **Doctor Verify OTP** - Verify email OTP
- **Doctor Login** - Login with credentials
- **Doctor Forgot Password** - Request password reset
- **Doctor Reset Password** - Reset password with OTP
- **Patient Signup** - Register new patient

### 2️⃣ Doctor Profile
- **Get Doctor Profile** - Get doctor details
- **Update Doctor Profile** - Update doctor info
- **Complete Doctor Profile** - Complete profile with all fields
- **Get Doctor Profile Fields** - Get available profile fields

### 3️⃣ Patient Selection (NEW)
- **Get All Doctors** - Browse doctors with patient counts
- **Search Doctors** - Advanced filtering
- **Get Public Doctor Profile** - Public doctor details

### 4️⃣ Appointments CRUD
- **Get All Appointments** - List all appointments
- **Get Patient Appointments** - Filter by patient ID ✨
- **Get Single Appointment by ID** - Get specific appointment ✨ NEW
- **Create Appointment** - Create new appointment
- **Create Video Call Appointment** - Create online appointment
- **Update Appointment** - Update appointment details
- **Delete Appointment** - Remove appointment

### 5️⃣ Doctor Dashboard
- **Get Dashboard Stats** - Dashboard statistics
- **Get Doctor Patients** - List all patients
- **Get Patient Details** - Patient information
- **Get Patient Full Details** - Comprehensive patient data
- **Get Patient AI Summary** - AI-generated summary

### 6️⃣ Patient Health Data ✨
- **Get Medication History** - Patient medication records
- **Get Food Entries (Nutrition)** - Nutrition tracking data
- **Get Mental Health History** - Mental health logs
- **Get Kick Count History** - Pregnancy kick count logs
- **Get Prescription Documents** - Prescription files
- **Get Vital Signs History** - Vital signs measurements

### 7️⃣ Patient CRUD
- **Get All Patients** - List patients with pagination
- **Get Patient by ID** - Get specific patient
- **Create Patient** - Add new patient
- **Update Patient** - Update patient info
- **Delete Patient** - Remove patient

### 8️⃣ Health Check
- **Root Endpoint** - API information
- **Health Check** - API health status

---

## 🎯 Complete Testing Flow

### **Flow 1: Doctor Registration & Login**
```
1. Doctor Signup → Get signup_token
2. Check email for OTP
3. Doctor Verify OTP → Get access_token & doctor_id
4. Doctor Login → Get access_token (for future logins)
```

### **Flow 2: Patient Appointment Management**
```
1. Get All Appointments → View all appointments
2. Get Patient Appointments → Filter by patient_id
3. Create Appointment → New appointment
4. Update Appointment → Modify details
5. Delete Appointment → Remove appointment
```

### **Flow 3: Patient Selection**
```
1. Get All Doctors → Browse available doctors
2. Search Doctors → Filter by specialization/city
3. Get Public Doctor Profile → View doctor details with patient count
4. Create Appointment → Book with selected doctor
```

---

## 📊 Appointment API Details

### **Get Appointments for Specific Patient** ✨

**Endpoint:**
```
GET /doctor/appointments?patient_id={patient_id}
```

**Example Request:**
```bash
GET http://localhost:8000/doctor/appointments?patient_id=PAT17576730523DFD2A
```

**Response:**
```json
{
  "success": true,
  "appointments": [
    {
      "appointment_id": "68d57d8052eb7b568d9a0848",
      "patient_id": "PAT17576730523DFD2A",
      "patient_name": "kdkdkkr",
      "appointment_date": "2025-01-26",
      "appointment_time": "10:00 AM",
      "appointment_type": "Consultation",
      "appointment_status": "scheduled",
      "notes": "Test appointment",
      "doctor_id": "",
      "created_at": "2025-09-25T23:06:00.061633",
      "updated_at": "2025-09-25T23:06:00.061979",
      "status": "active"
    }
  ],
  "total_count": 1
}
```

### **Get Single Appointment by ID** ✨ NEW

**Endpoint:**
```
GET /doctor/appointments/{appointment_id}
```

**Example Request:**
```bash
GET http://localhost:8000/doctor/appointments/68e6494cb0724d5e547834dc
```

**Response:**
```json
{
  "success": true,
  "appointment": {
    "appointment_id": "68e6494cb0724d5e547834dc",
    "patient_id": "PAT17576730523DFD2A",
    "patient_name": "kdkdkkr",
    "appointment_date": "2024-12-20",
    "appointment_time": "3:00 PM",
    "appointment_type": "Follow-up",
    "appointment_status": "scheduled",
    "notes": "Test single appointment GET",
    "doctor_id": "",
    "created_at": "2025-10-08T16:51:48.970459",
    "updated_at": "2025-10-08T16:51:48.970602",
    "status": "active"
  }
}
```

### **All Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `patient_id` | string | Filter by patient | `?patient_id=PAT123456` |
| `date` | string | Filter by date | `?date=2025-01-15` |
| `status` | string | Filter by status | `?status=scheduled` |

---

## 🔐 Authentication

### Public Endpoints (No Auth Required)
- All authentication endpoints (signup, login, forgot password)
- Patient selection endpoints (`/doctors`, `/doctors/search`)
- Health check endpoints

### Protected Endpoints (Auth Required)
- Doctor profile endpoints
- Appointment CRUD operations
- Patient CRUD operations
- Dashboard endpoints

**Use this header for protected endpoints:**
```json
{
  "Authorization": "Bearer {{access_token}}"
}
```

---

## 📝 Request & Response Examples

### **1. Doctor Signup**
**Request:**
```json
{
  "username": "TestDoctor",
  "email": "test.doctor@example.com",
  "mobile": "9876543210",
  "password": "TestPass123!",
  "role": "doctor"
}
```

**Response (200):**
```json
{
  "email": "test.doctor@example.com",
  "message": "Please check your email for OTP verification.",
  "signup_token": "eyJhbGciOiJIUzI1NiIs...",
  "status": "otp_sent"
}
```

### **2. Doctor Verify OTP**
**Request:**
```json
{
  "email": "test.doctor@example.com",
  "otp": "123456",
  "jwt_token": "{{signup_token}}",
  "role": "doctor"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Doctor account created successfully!",
  "doctor_id": "D17597286260221902",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "status": "pending_profile"
}
```

### **3. Create Appointment**
**Request:**
```json
{
  "patient_id": "PAT123456",
  "appointment_date": "2024-01-15",
  "appointment_time": "10:00 AM",
  "appointment_type": "General",
  "appointment_mode": "in-person",
  "notes": "Regular checkup"
}
```

**Response (201):**
```json
{
  "appointment_id": "68e615d5166ba6407219b671",
  "message": "Appointment created successfully"
}
```

### **4. Update Appointment**
**Request:**
```json
{
  "appointment_time": "2:00 PM",
  "appointment_status": "rescheduled",
  "notes": "Updated appointment time"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Appointment updated successfully",
  "appointment_id": "68e615d5166ba6407219b671"
}
```

### **5. Get Patient Appointments**
**Request:**
```
GET /doctor/appointments?patient_id=PAT17576730523DFD2A
```

**Response (200):**
```json
{
  "success": true,
  "appointments": [
    {
      "appointment_id": "68d57d8052eb7b568d9a0848",
      "patient_id": "PAT17576730523DFD2A",
      "patient_name": "kdkdkkr",
      "appointment_date": "2025-01-26",
      "appointment_time": "10:00 AM",
      "appointment_type": "Consultation",
      "appointment_status": "scheduled",
      "notes": "Test appointment"
    }
  ],
  "total_count": 1
}
```

---

## 🎨 Appointment Mode Support

### **Appointment Modes Available:**

| Mode | Value | Description |
|------|-------|-------------|
| In-Person | `in-person` | Physical clinic visit (default) |
| Video Call | `video-call` | Online video consultation |
| Phone Call | `phone-call` | Phone consultation |
| Home Visit | `home-visit` | Doctor visits patient's home |

### **Create Video Call Appointment:**
```json
{
  "patient_id": "PAT123456",
  "appointment_date": "2024-01-16",
  "appointment_time": "2:00 PM",
  "appointment_type": "Follow-up",
  "appointment_mode": "video-call",
  "video_link": "https://meet.google.com/abc-defg-hij",
  "notes": "Online consultation"
}
```

---

## 📊 Field Reference

### **Appointment Fields**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `patient_id` | string | ✅ Yes | Patient identifier |
| `appointment_date` | string | ✅ Yes | Date (YYYY-MM-DD) |
| `appointment_time` | string | ✅ Yes | Time (HH:MM AM/PM) |
| `appointment_type` | string | ⚪ No | General, Follow-up, etc. (default: "General") |
| `appointment_mode` | string | ⚪ No | in-person, video-call, etc. (default: "in-person") |
| `video_link` | string | ⚪ No | Video call URL (for video-call mode) |
| `notes` | string | ⚪ No | Additional notes |
| `doctor_id` | string | ⚪ No | Doctor identifier |

### **Doctor Signup Fields**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `username` | string | ✅ Yes | Unique username |
| `email` | string | ✅ Yes | Valid email address |
| `mobile` | string | ✅ Yes | Mobile number |
| `password` | string | ✅ Yes | Account password |
| `role` | string | ⚪ No | Role type (default: "doctor") |

### **Doctor Login Fields**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `email` | string | ✅ Yes | Email or doctor_id |
| `password` | string | ✅ Yes | Account password |

---

## 🧪 Testing Examples

### **PowerShell:**

```powershell
# Get all appointments
Invoke-RestMethod -Uri "http://localhost:8000/doctor/appointments"

# Get appointments for specific patient
Invoke-RestMethod -Uri "http://localhost:8000/doctor/appointments?patient_id=PAT17576730523DFD2A"

# Create appointment
$body = @{
    patient_id = "PAT123456"
    appointment_date = "2024-01-15"
    appointment_time = "10:00 AM"
    appointment_type = "General"
    notes = "Regular checkup"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/doctor/appointments" -Method POST -Body $body -ContentType "application/json"

# Update appointment
$updateBody = @{
    appointment_time = "2:00 PM"
    appointment_status = "rescheduled"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/doctor/appointments/68e615d5166ba6407219b671" -Method PUT -Body $updateBody -ContentType "application/json"

# Delete appointment
Invoke-RestMethod -Uri "http://localhost:8000/doctor/appointments/68e615d5166ba6407219b671" -Method DELETE
```

---

## 🎯 Key Features

### ✅ Complete CRUD Operations
- **Appointments**: Full CRUD (Create, Read, Update, Delete)
- **Patients**: Full CRUD support
- **Doctors**: Profile management

### ✅ Advanced Filtering
- Filter appointments by patient_id
- Filter appointments by date
- Filter appointments by status
- Search doctors by specialization/city

### ✅ Patient Count Integration
- Each doctor shows current patient count
- Helps patients choose experienced doctors
- Real-time patient statistics

### ✅ Appointment Modes
- Support for in-person visits
- Support for video call consultations
- Support for phone consultations
- Optional video link for online appointments

---

## 📌 Status Codes

| Code | Description |
|------|-------------|
| 200 | Success (GET, PUT, DELETE) |
| 201 | Created (POST) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid credentials) |
| 404 | Not Found |
| 500 | Server Error |

---

## 🔄 Workflow Examples

### **Complete Doctor Onboarding:**
1. **Doctor Signup** → Get `signup_token`
2. **Verify OTP** → Get `access_token` & `doctor_id`
3. **Complete Profile** → Add professional details
4. **View Dashboard** → See statistics

### **Appointment Management:**
1. **Get All Appointments** → View all
2. **Filter by Patient** → Use `?patient_id=PAT123456`
3. **Create Appointment** → Add new
4. **Update Appointment** → Modify details
5. **Delete Appointment** → Remove

### **Patient Selection:**
1. **Browse Doctors** → `GET /doctors`
2. **Search by Specialization** → `GET /doctors/search?specialization=cardiology`
3. **View Doctor Profile** → `GET /doctors/{doctor_id}`
4. **Create Appointment** → Book with selected doctor

---

## 📱 Flutter Integration Examples

### **Get Patient Appointments:**
```dart
Future<Map<String, dynamic>> getPatientAppointments(String patientId) async {
  final response = await http.get(
    Uri.parse('$baseUrl/doctor/appointments?patient_id=$patientId'),
    headers: {'Authorization': 'Bearer $accessToken'},
  );
  return json.decode(response.body);
}
```

### **Create Appointment:**
```dart
Future<Map<String, dynamic>> createAppointment({
  required String patientId,
  required String date,
  required String time,
  String? type,
  String? mode,
  String? notes,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/doctor/appointments'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode({
      'patient_id': patientId,
      'appointment_date': date,
      'appointment_time': time,
      'appointment_type': type ?? 'General',
      'appointment_mode': mode ?? 'in-person',
      'notes': notes ?? '',
    }),
  );
  return json.decode(response.body);
}
```

### **Update Appointment:**
```dart
Future<Map<String, dynamic>> updateAppointment(
  String appointmentId,
  Map<String, dynamic> updates,
) async {
  final response = await http.put(
    Uri.parse('$baseUrl/doctor/appointments/$appointmentId'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: json.encode(updates),
  );
  return json.decode(response.body);
}
```

### **Delete Appointment:**
```dart
Future<Map<String, dynamic>> deleteAppointment(String appointmentId) async {
  final response = await http.delete(
    Uri.parse('$baseUrl/doctor/appointments/$appointmentId'),
    headers: {'Authorization': 'Bearer $accessToken'},
  );
  return json.decode(response.body);
}
```

---

## 🔍 Query Parameters Guide

### **Appointments Filtering:**
```
# All appointments
GET /doctor/appointments

# Specific patient
GET /doctor/appointments?patient_id=PAT123456

# Specific date
GET /doctor/appointments?date=2024-01-15

# Scheduled appointments only
GET /doctor/appointments?status=scheduled

# Combined filters
GET /doctor/appointments?patient_id=PAT123456&date=2024-01-15&status=scheduled
```

### **Doctor Search:**
```
# All doctors
GET /doctors?page=1&limit=20

# Search by specialization
GET /doctors/search?specialization=cardiology

# Search by city
GET /doctors/search?city=mumbai

# Minimum patient count
GET /doctors/search?min_patients=10

# Combined filters
GET /doctors/search?specialization=cardiology&city=mumbai&min_patients=10
```

---

## 🎨 Appointment Mode Usage

### **In-Person Appointment:**
```json
{
  "patient_id": "PAT123456",
  "appointment_date": "2024-01-15",
  "appointment_time": "10:00 AM",
  "appointment_type": "General",
  "appointment_mode": "in-person",
  "notes": "Regular checkup at clinic"
}
```

### **Video Call Appointment:**
```json
{
  "patient_id": "PAT123456",
  "appointment_date": "2024-01-16",
  "appointment_time": "2:00 PM",
  "appointment_type": "Follow-up",
  "appointment_mode": "video-call",
  "video_link": "https://meet.google.com/abc-defg-hij",
  "notes": "Online consultation"
}
```

---

## 🚨 Error Handling

### **Common Errors:**

**400 - Bad Request**
```json
{
  "error": "patient_id is required"
}
```

**401 - Unauthorized**
```json
{
  "error": "Invalid credentials"
}
```

**404 - Not Found**
```json
{
  "error": "Appointment not found"
}
```

**500 - Server Error**
```json
{
  "error": "Server error: Database connection failed"
}
```

---

## 📊 API Endpoint Summary

### **Authentication Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/doctor-signup` | Register doctor |
| POST | `/doctor-verify-otp` | Verify OTP |
| POST | `/doctor-login` | Login doctor |
| POST | `/doctor-forgot-password` | Forgot password |
| POST | `/doctor-reset-password` | Reset password |

### **Doctor Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/profile/{id}` | Get doctor profile |
| PUT | `/doctor/profile/{id}` | Update doctor profile |
| POST | `/doctor-complete-profile` | Complete profile |
| GET | `/doctor-profile-fields` | Get profile fields |

### **Patient Selection**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctors` | List all doctors |
| GET | `/doctors/search` | Search doctors |
| GET | `/doctors/{id}` | Get public doctor profile |

### **Appointments CRUD** ✨
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/appointments` | Get all appointments |
| GET | `/doctor/appointments?patient_id={id}` | Get patient appointments |
| GET | `/doctor/appointments/{appointment_id}` | Get single appointment by ID ✨ |
| POST | `/doctor/appointments` | Create appointment |
| PUT | `/doctor/appointments/{id}` | Update appointment |
| DELETE | `/doctor/appointments/{id}` | Delete appointment |

### **Dashboard**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/dashboard-stats` | Dashboard stats |
| GET | `/doctor/patients` | List patients |
| GET | `/doctor/patient/{id}` | Patient details |
| GET | `/doctor/patient/{id}/full-details` | Full patient data |
| GET | `/doctor/patient/{id}/ai-summary` | AI summary |

### **Patient Health Data** ✨
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/medication/get-medication-history/{patient_id}` | Medication history |
| GET | `/nutrition/get-food-entries/{patient_id}` | Nutrition/food entries |
| GET | `/mental-health/history/{patient_id}` | Mental health logs |
| GET | `/kick-count/get-kick-history/{patient_id}` | Kick count history |
| GET | `/prescription/documents/{patient_id}` | Prescription documents |
| GET | `/vital-signs/history/{patient_id}` | Vital signs history |

---

## ✅ All Features Included

- ✅ Complete Authentication System
- ✅ Doctor Profile Management
- ✅ Patient Selection with Patient Count
- ✅ **Full Appointment CRUD Operations**
- ✅ **Single Appointment GET by ID**
- ✅ **Patient-specific Appointment Filtering**
- ✅ Dashboard Statistics
- ✅ Patient Management
- ✅ **Patient Health Data Endpoints** (Medication, Nutrition, Mental Health, Kick Count, Prescriptions, Vital Signs)
- ✅ Appointment Mode Support (in-person, video-call)

---

## 🎉 Ready to Use!

Import the collection into Postman and start testing all your APIs immediately!

**Happy Testing! 🚀**
