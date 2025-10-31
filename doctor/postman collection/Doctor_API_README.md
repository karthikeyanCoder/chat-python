# Doctor API Collection - Postman Documentation

## 📋 Overview

This Postman collection contains all Doctor-related APIs including the new **Patient Selection APIs** for browsing and selecting doctors. The collection is organized into logical groups for easy testing and development.

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click "Import" → "Upload Files"
3. Select `Doctor_API_Postman_Collection.json`
4. Click "Import"

### 2. Set Environment Variables
The collection includes these variables:
- `base_url`: `http://localhost:8000` (default)
- `doctor_id`: Sample doctor ID for testing
- `access_token`: JWT token for authenticated requests

### 3. Start Testing
Begin with the "Doctor Authentication" folder to create a doctor account.

## 📁 Collection Structure

### 🔐 Doctor Authentication
- **Doctor Signup** - Register new doctor account
- **Doctor Verify OTP** - Verify email OTP
- **Doctor Login** - Login with credentials
- **Doctor Forgot Password** - Request password reset
- **Doctor Reset Password** - Reset password with OTP

### 👤 Doctor Profile Management
- **Get Doctor Profile** - Get detailed doctor profile (authenticated)
- **Update Doctor Profile** - Update doctor information
- **Complete Doctor Profile** - Complete profile with all fields
- **Get Doctor Profile Fields** - Get available profile fields

### 🆕 Patient Selection APIs (NEW)
**These are the new APIs for patient doctor selection:**

#### Get All Doctors (Patient Selection)
```
GET /doctors?page=1&limit=20
```
**Query Parameters:**
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)
- `search` - Search in name, email, specialization
- `specialization` - Filter by medical specialization
- `city` - Filter by city
- `min_patients` - Minimum patient count

**Response:**
```json
{
  "success": true,
  "doctors": [
    {
      "doctor_id": "D17597286260221902",
      "first_name": "Rama",
      "last_name": "A",
      "specialization": "Obstetrics",
      "city": "New York",
      "experience_years": 0,
      "consultation_fee": 0,
      "patient_count": 0,
      "hospital_name": "",
      "languages": [],
      "qualifications": []
    }
  ],
  "total_count": 3,
  "page": 1,
  "limit": 20,
  "total_pages": 1,
  "filters_applied": {
    "search": "",
    "specialization": "",
    "city": "",
    "min_patients": ""
  }
}
```

#### Search Doctors with Filters
```
GET /doctors/search?specialization=cardiology&city=mumbai&min_patients=10
```
Same as above but with advanced filtering capabilities.

#### Get Public Doctor Profile
```
GET /doctors/{doctor_id}
```
Get public doctor profile for patient selection (no sensitive data).

### 🏥 Doctor Dashboard & Patients
- **Get Doctor Patients** - List all patients for doctor
- **Get Patient Details** - Get specific patient information
- **Get Patient Full Details** - Get comprehensive patient data
- **Get Patient AI Summary** - Get AI-generated patient summary
- **Get Dashboard Stats** - Get doctor dashboard statistics

### 📅 Doctor Appointments
- **Get Doctor Appointments** - List all appointments
- **Create Appointment** - Create new appointment

### 🐛 Debug & Testing
- **Debug Doctors** - Debug endpoint for doctor data
- **Test Login** - Test login functionality

## 🔍 API Endpoints Summary

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/doctor-signup` | Register new doctor |
| POST | `/doctor-verify-otp` | Verify OTP |
| POST | `/doctor-login` | Login doctor |
| POST | `/doctor-forgot-password` | Forgot password |
| POST | `/doctor-reset-password` | Reset password |

### Profile Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/profile/{doctor_id}` | Get doctor profile |
| PUT | `/doctor/profile/{doctor_id}` | Update doctor profile |
| POST | `/doctor/complete-profile` | Complete profile |
| GET | `/doctor-profile-fields` | Get profile fields |

### 🆕 Patient Selection APIs (NEW)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctors` | Get all doctors for selection |
| GET | `/doctors/search` | Search doctors with filters |
| GET | `/doctors/{doctor_id}` | Get public doctor profile |

### Dashboard & Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/patients` | Get doctor's patients |
| GET | `/doctor/patient/{patient_id}` | Get patient details |
| GET | `/doctor/patient/{patient_id}/full-details` | Get full patient details |
| GET | `/doctor/patient/{patient_id}/ai-summary` | Get AI summary |
| GET | `/doctor/dashboard-stats` | Get dashboard stats |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctor/appointments` | Get appointments |
| POST | `/doctor/appointments` | Create appointment |

## 🎯 Patient Selection Flow

### 1. Browse Doctors
```
GET /doctors
```
Returns list of all available doctors with patient counts.

### 2. Search/Filter Doctors
```
GET /doctors/search?specialization=cardiology&city=mumbai&min_patients=10
```
Filter doctors by specialization, city, and minimum patient count.

### 3. View Doctor Profile
```
GET /doctors/{doctor_id}
```
Get detailed public profile of selected doctor.

### 4. Select Doctor
Use the doctor information to create appointments or assign patients.

## 📊 Key Features

### ✅ Patient Count Integration
- Each doctor shows their current patient count
- Helps patients choose experienced doctors
- Shows doctor popularity and capacity

### ✅ Advanced Filtering
- Filter by specialization (Cardiology, Neurology, etc.)
- Filter by city/location
- Filter by minimum patient count
- Search by name or email

### ✅ Pagination Support
- Page-based pagination
- Configurable page size
- Total count and page information

### ✅ Public vs Private Profiles
- Public profiles for patient selection (no sensitive data)
- Private profiles for authenticated doctor access
- Secure separation of concerns

## 🔧 Testing Examples

### Example 1: Get All Doctors
```bash
curl -X GET "http://localhost:8000/doctors?page=1&limit=5"
```

### Example 2: Search Cardiology Doctors
```bash
curl -X GET "http://localhost:8000/doctors/search?specialization=cardiology&min_patients=5"
```

### Example 3: Get Doctor Profile
```bash
curl -X GET "http://localhost:8000/doctors/D17597286260221902"
```

### Example 4: Filter by City
```bash
curl -X GET "http://localhost:8000/doctors?city=mumbai&min_patients=10"
```

## 🚨 Error Handling

### Common Error Responses

#### 404 - Doctor Not Found
```json
{
  "error": "Doctor not found"
}
```

#### 400 - Bad Request
```json
{
  "error": "Doctor ID is required"
}
```

#### 500 - Server Error
```json
{
  "error": "Server error: Database connection failed"
}
```

## 🔐 Authentication

### Public Endpoints (No Auth Required)
- `GET /doctors` - Browse doctors
- `GET /doctors/search` - Search doctors
- `GET /doctors/{doctor_id}` - Public doctor profile
- `GET /doctor-profile-fields` - Profile fields

### Protected Endpoints (Auth Required)
- All `/doctor/profile/*` endpoints
- All `/doctor/patients/*` endpoints
- All `/doctor/appointments/*` endpoints
- Dashboard and stats endpoints

**Use the `Authorization: Bearer {access_token}` header for protected endpoints.**

## 📝 Notes

1. **Patient Count**: The `patient_count` field shows how many patients are currently assigned to each doctor.

2. **Pagination**: Use `page` and `limit` parameters for large result sets.

3. **Search**: The `search` parameter searches across name, email, and specialization fields.

4. **Filters**: Multiple filters can be combined for precise results.

5. **Public Profiles**: Public doctor profiles exclude sensitive information like email and mobile numbers.

## 🎉 Ready to Use!

The collection is ready for immediate use. Import it into Postman and start testing the complete doctor API system including the new patient selection features!

**Happy Testing! 🚀**
