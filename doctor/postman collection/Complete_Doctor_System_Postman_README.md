# Complete Doctor Patient Management System - Postman Collection

## 📋 Overview

This comprehensive Postman collection includes all API endpoints for the Doctor Patient Management System with sample inputs and expected outputs for each endpoint.

## 🚀 Quick Start

### 1. Import the Collection
1. Open Postman
2. Click "Import" 
3. Select `Complete_Doctor_System_Postman_Collection.json`
4. The collection will be imported with all endpoints organized in folders

### 2. Set Environment Variables
The collection uses these variables (set them in Postman environment or collection variables):

```json
{
  "baseUrl": "http://localhost:5000",
  "authToken": "",
  "doctorId": "",
  "patientId": ""
}
```

### 3. Authentication Flow
1. **Login** → Get token from response
2. **Set authToken** → Copy token to `{{authToken}}` variable
3. **Set doctorId** → Copy doctor_id from login response
4. **Use other endpoints** → All protected endpoints will use the token

## 📁 Collection Structure

### 1. Health Check
- **GET /health** - Check server status

### 2. Authentication
- **POST /login** - Doctor login
- **PUT /doctor/{doctorId}/profile** - Update doctor profile

### 3. Patient CRUD Operations
- **POST /patients** - Create new patient
- **GET /patients/{patientId}** - Get patient by ID
- **GET /patients** - Get all patients (with pagination)
- **PUT /patients/{patientId}** - Update patient
- **DELETE /patients/{patientId}** - Delete patient

### 4. Doctor Dashboard & Patient Data
- **GET /doctor/{doctorId}/dashboard** - Get dashboard statistics
- **GET /doctor/patient/{patientId}/full-details** - Get complete patient data
- **GET /doctor/patient/{patientId}/ai-summary** - Get AI-generated patient summary

### 5. Appointment Management
- **POST /appointments** - Create appointment
- **GET /doctor/{doctorId}/appointments** - Get doctor's appointments

### 6. Health Data Endpoints
- **GET /patients/{patientId}/medications** - Get patient medications
- **GET /patients/{patientId}/symptoms** - Get patient symptoms
- **GET /patients/{patientId}/food-entries** - Get patient food entries
- **GET /patients/{patientId}/mental-health** - Get mental health logs
- **GET /patients/{patientId}/vital-signs** - Get vital signs logs

## 🔧 Sample API Calls

### 1. Doctor Login
```http
POST http://localhost:5000/login
Content-Type: application/json

{
  "email": "ramyayashva@gmail.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "doctor_id": "D17587987732214",
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "email": "ramyayashva@gmail.com",
    "specialization": "General Medicine"
  }
}
```

### 2. Create New Patient
```http
POST http://localhost:5000/patients
Content-Type: application/json

{
  "full_name": "John Doe",
  "date_of_birth": "15/03/1985",
  "contact_number": "9876543210",
  "email": "john.doe@example.com",
  "gender": "Male",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_number": "9876543211",
  "medical_notes": "No known conditions",
  "allergies": "None",
  "blood_type": "O+",
  "assigned_doctor_id": "D17587987732214",
  "is_active": true
}
```

**Response:**
```json
{
  "message": "Patient created successfully",
  "patient_id": "PAT1758894320123456",
  "status": "success"
}
```

### 3. Get Patient Full Details
```http
GET http://localhost:5000/doctor/patient/PAT1758894320123456/full-details
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "patient_info": {
    "patient_id": "PAT1758894320123456",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "contact_number": "9876543210",
    "date_of_birth": "15/03/1985",
    "gender": "Male",
    "blood_type": "O+",
    "allergies": "None",
    "medical_notes": "No known conditions"
  },
  "health_data": {
    "medication_history": [],
    "symptom_reports": [...],
    "food_entries": [...],
    "mental_health_logs": [...],
    "kick_count_logs": [],
    "vital_signs_logs": [...]
  },
  "summary": {
    "total_medications": 0,
    "total_symptoms": 1,
    "total_food_entries": 1,
    "total_mental_health_logs": 1,
    "total_kick_counts": 0,
    "total_vital_signs": 1
  }
}
```

### 4. Get AI Summary
```http
GET http://localhost:5000/doctor/patient/PAT1758894320123456/ai-summary
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "ai_summary": "Patient John Doe is a 40-year-old male with blood type O+. Recent health data shows: 1 symptom report indicating possible viral infection with headache and fever. Patient maintains good mental health with positive mood and low stress levels. Dietary habits include healthy choices like apples. Vital signs are within normal range (BP: 120/80, HR: 72, Temp: 98.6°F). No current medications or allergies reported. Overall health status appears stable with no immediate concerns.",
  "patient_id": "PAT1758894320123456",
  "generated_at": "2025-09-26T18:45:00Z"
}
```

## 🔐 Authentication

Most endpoints require authentication. Follow these steps:

1. **Login first** using `/login` endpoint
2. **Copy the token** from the response
3. **Set the token** in Postman environment variable `authToken`
4. **Use Authorization header** in protected endpoints:
   ```
   Authorization: Bearer {{authToken}}
   ```

## 📊 Data Validation

### Required Fields for Patient Creation:
- `full_name` (string, required)
- `date_of_birth` (string, required)
- `contact_number` (string, min 10 digits, required)
- `email` (string, valid email format, required)

### Optional Fields:
- `gender`, `address`, `city`, `state`, `pincode`
- `emergency_contact_name`, `emergency_contact_number`
- `medical_notes`, `allergies`, `blood_type`
- `assigned_doctor_id`, `is_active`

## 🚨 Error Responses

### Common Error Codes:
- **400 Bad Request** - Invalid input data
- **401 Unauthorized** - Missing or invalid token
- **404 Not Found** - Resource not found
- **409 Conflict** - Resource already exists (e.g., duplicate email)
- **500 Internal Server Error** - Server error

### Sample Error Response:
```json
{
  "error": "Missing required field: email"
}
```

## 🧪 Testing Workflow

### 1. Basic Flow:
1. Health check → Verify server is running
2. Login → Get authentication token
3. Create patient → Get patient ID
4. Get patient details → Verify data
5. Get AI summary → Test OpenAI integration

### 2. Complete CRUD Flow:
1. Create patient
2. Get patient by ID
3. Update patient
4. Get all patients
5. Delete patient

### 3. Health Data Flow:
1. Create patient
2. Get patient medications
3. Get patient symptoms
4. Get patient food entries
5. Get mental health logs
6. Get vital signs
7. Get full patient details
8. Get AI summary

## 🔧 Environment Setup

### Prerequisites:
- Backend server running on `http://localhost:5000`
- MongoDB database connected
- OpenAI API key configured in `.env` file

### Environment Variables:
```bash
# .env file
MONGODB_URI=mongodb://localhost:27017/doctor_db
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
PORT=5000
```

## 📝 Notes

1. **Patient ID Format**: `PAT` + timestamp + random string
2. **Doctor ID Format**: `D` + timestamp + random string
3. **Appointment ID Format**: `APT` + timestamp + random string
4. **All timestamps** are in ISO 8601 format
5. **Pagination** is supported for list endpoints
6. **Search functionality** available for patient lists

## 🆘 Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Ensure backend server is running on port 5000
   - Check if MongoDB is connected

2. **401 Unauthorized**
   - Verify token is set correctly
   - Check if token has expired
   - Re-login to get fresh token

3. **404 Not Found**
   - Verify patient/doctor ID exists
   - Check URL path is correct

4. **500 Internal Server Error**
   - Check server logs
   - Verify database connection
   - Check environment variables

### Debug Steps:
1. Check server logs: `python app_mvc.py`
2. Verify database connection
3. Test individual endpoints
4. Check environment variables
5. Validate request data format

## 📞 Support

For issues or questions:
1. Check server logs first
2. Verify all environment variables
3. Test with provided sample data
4. Check MongoDB connection
5. Validate request/response format

---

**Happy Testing! 🚀**
