# Appointment Management API - Postman Collection

This Postman collection provides comprehensive testing for appointment management endpoints in the Doctor-Patient System.

## 📋 Collection Overview

The collection includes:
- **Authentication**: Doctor login to get JWT token
- **Appointment CRUD Operations**: Create, Read, Update, Delete appointments
- **Automatic Token Management**: Automatically saves and uses authentication tokens
- **Sample Data**: Pre-configured with realistic test data

## 🚀 Quick Start

### 1. Import the Collection
1. Open Postman
2. Click "Import" button
3. Select `Appointment_Management_Postman_Collection.json`
4. The collection will be imported with all endpoints

### 2. Set Environment Variables
The collection uses these variables:
- `baseUrl`: `http://localhost:5000` (or your server URL)
- `authToken`: Automatically set after login
- `appointmentId`: Automatically set from API responses

### 3. Test Authentication
1. Run "Doctor Login" request
2. The token will be automatically saved for other requests

### 4. Test Appointment Operations
1. **Get All Appointments** - Retrieve existing appointments
2. **Create New Appointment** - Add a new appointment
3. **Update Appointment** - Modify appointment details
4. **Delete Appointment** - Remove an appointment
5. **Get Appointment by ID** - Retrieve specific appointment

## 📝 API Endpoints

### Authentication
- **POST** `/doctor-login` - Login to get JWT token

### Appointment Management
- **GET** `/doctor/appointments` - Get all appointments
- **POST** `/doctor/appointments` - Create new appointment
- **PUT** `/doctor/appointments/{appointment_id}` - Update appointment
- **DELETE** `/doctor/appointments/{appointment_id}` - Delete appointment
- **GET** `/doctor/appointments/{appointment_id}` - Get specific appointment

## 🔧 Request Examples

### Create Appointment
```json
{
  "patient_id": "PAT1758712159E182A3",
  "appointment_date": "2025-01-30",
  "appointment_time": "14:30:00",
  "appointment_type": "follow-up",
  "notes": "Follow-up appointment for medication review",
  "duration_minutes": 30
}
```

### Update Appointment
```json
{
  "appointment_date": "2025-01-31",
  "appointment_time": "15:00:00",
  "appointment_type": "consultation",
  "status": "confirmed",
  "notes": "Updated appointment time - patient requested change",
  "duration_minutes": 45
}
```

## 📊 Response Examples

### Successful Login
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "doctor": {
    "doctor_id": "D17587987732214",
    "username": "ramya",
    "email": "ramyayashva@gmail.com",
    "role": "doctor"
  }
}
```

### Appointment Created
```json
{
  "success": true,
  "message": "Appointment created successfully",
  "appointment_id": "APT1758712159E182A4",
  "appointment": {
    "appointment_id": "APT1758712159E182A4",
    "patient_id": "PAT1758712159E182A3",
    "doctor_id": "D17587987732214",
    "appointment_date": "2025-01-30",
    "appointment_time": "14:30:00",
    "appointment_type": "follow-up",
    "status": "scheduled",
    "notes": "Follow-up appointment for medication review",
    "duration_minutes": 30,
    "created_at": "2025-01-27T16:45:00Z"
  }
}
```

## 🔐 Authentication

All appointment endpoints require authentication:
- Include `Authorization: Bearer {token}` header
- Token is automatically managed by the collection
- Token expires after 15 minutes (refresh by re-logging in)

## ⚠️ Important Notes

### Missing Endpoints
The current backend only has GET and POST endpoints for appointments. The PUT and DELETE endpoints in this collection are **not yet implemented** in your backend. You would need to add these endpoints to `app_mvc.py` and implement the corresponding methods in `doctor_controller.py`.

### Required Backend Implementation
To support the PUT and DELETE operations, you need to add:

1. **Routes in `app_mvc.py`:**
```python
@app.route('/doctor/appointments/<appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    return doctor_controller.update_appointment(request, appointment_id)

@app.route('/doctor/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    return doctor_controller.delete_appointment(request, appointment_id)

@app.route('/doctor/appointments/<appointment_id>', methods=['GET'])
def get_appointment_by_id(appointment_id):
    return doctor_controller.get_appointment_by_id(request, appointment_id)
```

2. **Methods in `doctor_controller.py`:**
```python
def update_appointment(self, request, appointment_id: str) -> tuple:
    # Implementation needed

def delete_appointment(self, request, appointment_id: str) -> tuple:
    # Implementation needed

def get_appointment_by_id(self, request, appointment_id: str) -> tuple:
    # Implementation needed
```

## 🧪 Testing Workflow

1. **Start your server**: `python app_mvc.py`
2. **Import collection** into Postman
3. **Run "Doctor Login"** to get authentication token
4. **Test existing endpoints** (GET, POST) to verify they work
5. **Implement missing endpoints** (PUT, DELETE) in your backend
6. **Test complete CRUD operations** once implemented

## 📱 Sample Test Data

The collection includes realistic test data:
- **Patient ID**: `PAT1758712159E182A3`
- **Doctor ID**: `D17587987732214`
- **Appointment Types**: `consultation`, `follow-up`, `emergency`
- **Statuses**: `scheduled`, `confirmed`, `completed`, `cancelled`

## 🔍 Error Handling

The collection includes examples of common error responses:
- **401 Unauthorized**: Invalid or missing token
- **404 Not Found**: Appointment doesn't exist
- **400 Bad Request**: Invalid input data
- **500 Server Error**: Internal server issues

## 📞 Support

If you encounter issues:
1. Ensure your server is running on `http://localhost:5000`
2. Check that authentication is working
3. Verify database connections are stable
4. Review server logs for detailed error messages
