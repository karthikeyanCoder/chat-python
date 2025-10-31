# Nurse Management API Documentation

This document provides details about the Nurse Management APIs in the Pregnancy AI system.

## Base URL
```
http://localhost:5000
```

## Authentication
All nurse management endpoints require authentication. Use the token received from the login endpoint in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### 1. Login
```
POST /doctor-login
```
Login endpoint for nurses to access the system.

**Request Body:**
```json
{
    "email": "nurse@example.com",
    "password": "password123",
    "role": "nurse"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "token": "<jwt_token>",
    "nurse_id": "N000001",
    "email": "nurse@example.com",
    "doctor_id": "<doctor_id>",
    "user": {
        "id": "N000001",
        "email": "nurse@example.com",
        "role": "nurse",
        "doctor_id": "<doctor_id>"
    }
}
```

### 2. Create Nurse
```
POST /api/nurses
```
Create a new nurse account. Only authenticated doctors can create nurses.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "nurse@example.com",
    "phone": "1234567890",
    "department": "Obstetrics",
    "shift": "Morning",
    "specialization": "Midwife",
    "experience_years": 5,
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "nurse": {
        "nurse_id": "N000001",
        "name": "John Doe",
        "email": "nurse@example.com",
        "phone": "1234567890",
        "department": "Obstetrics",
        "shift": "Morning",
        "specialization": "Midwife",
        "experience_years": 5,
        "assigned_doctor_id": "<doctor_id>",
        "created_at": "2025-10-27T10:00:00.000Z",
        "updated_at": "2025-10-27T10:00:00.000Z",
        "is_active": true
    },
    "message": "Nurse created successfully",
    "temporary_password": "password123" // Only included if password was auto-generated
}
```

### 3. Get All Nurses
```
GET /api/nurses
```
Get all nurses assigned to the logged-in doctor.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "nurses": [
        {
            "nurse_id": "N000001",
            "name": "John Doe",
            "email": "nurse@example.com",
            "phone": "1234567890",
            "department": "Obstetrics",
            "shift": "Morning",
            "specialization": "Midwife",
            "experience_years": 5,
            "assigned_doctor_id": "<doctor_id>",
            "created_at": "2025-10-27T10:00:00.000Z",
            "updated_at": "2025-10-27T10:00:00.000Z",
            "is_active": true
        }
    ],
    "total_count": 1
}
```

### 4. Delete Nurse
```
POST /api/nurses/delete
```
Delete a nurse by email. Only the assigned doctor can delete their nurses.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "email": "nurse@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Nurse with email nurse@example.com has been deleted"
}
```

### 5. Reset Nurse Password
```
POST /api/nurses/{nurse_id}/reset-password
```
Reset password for a specific nurse. Only the assigned doctor can reset their nurses' passwords.

**Request Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "new_password": "newpassword123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Password reset successfully"
}
```

## Error Responses
All endpoints may return the following error responses:

```json
{
    "error": "Authentication required"
}
```
Status: 401

```json
{
    "error": "Invalid credentials"
}
```
Status: 401

```json
{
    "error": "Nurse not found"
}
```
Status: 404

```json
{
    "error": "Database error: [error details]"
}
```
Status: 500

## Notes
1. All nurse accounts are associated with a doctor through the `assigned_doctor_id`
2. Each nurse has a unique `nurse_id` in the format N000001
3. Passwords are securely hashed using bcrypt before storage
4. The API supports both manual password setting and auto-generation
5. All timestamps are in ISO 8601 format