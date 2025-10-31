# 🎯 Dictation API - Postman Collection

## 📋 Overview

Complete Postman collection for testing the Dictation API with doctor-based storage system. All dictations are now stored in the `doctor_v2` collection based on the logged-in user (doctor).

---

## 🚀 Quick Start

### **1. Import Collection**
1. Open Postman
2. Click **Import** → **Upload Files**
3. Select `Dictation_API_Postman_Collection.json`
4. Collection imported successfully! ✅

### **2. Set Environment Variables**
Before testing, update these variables in Postman:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | Your API base URL |
| `patient_id` | `PAT175820015455746A` | Test patient ID |
| `doctor_jwt_token` | `YOUR_DOCTOR_JWT_TOKEN` | Doctor's JWT token |
| `patient_jwt_token` | `YOUR_PATIENT_JWT_TOKEN` | Patient's JWT token |

### **3. Get JWT Tokens**
You need valid JWT tokens to test the API:

```bash
# Login as Doctor
POST {{base_url}}/doctor/login
{
  "email": "doctor@example.com",
  "password": "doctor_password"
}

# Login as Patient  
POST {{base_url}}/patient/login
{
  "email": "patient@example.com", 
  "password": "patient_password"
}
```

---

## 📚 API Endpoints

### **1. Create Dictation**
**POST** `/doctor/patient/{patient_id}/dictations`

**Headers:**
```
Authorization: Bearer {doctor_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "language": "en",
  "text": "Patient reports feeling better today. Blood pressure is stable at 120/80."
}
```

**Success Response (201):**
```json
{
  "success": true,
  "dictation": {
    "dictation_id": "dict_1737542400000",
    "patient_id": "PAT175820015455746A",
    "language": "en",
    "text": "Patient reports feeling better today. Blood pressure is stable at 120/80.",
    "source": "doctor_dictation",
    "created_at": "2025-10-22T10:30:00.000Z",
    "updated_at": "2025-10-22T10:30:00.000Z"
  },
  "message": "Dictation saved"
}
```

### **2. List Dictations (Doctor View)**
**GET** `/doctor/patient/{patient_id}/dictations`

**Headers:**
```
Authorization: Bearer {doctor_jwt_token}
```

**Query Parameters:**
- `language` (optional): Filter by language (en, ta, hi, etc.)
- `from` (optional): Start date (ISO format)
- `to` (optional): End date (ISO format)
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Skip results (default: 0)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "dictation_id": "dict_1737542400000",
        "patient_id": "PAT175820015455746A",
        "language": "en",
        "text": "Patient reports feeling better today...",
        "source": "doctor_dictation",
        "created_at": "2025-10-22T10:30:00.000Z",
        "updated_at": "2025-10-22T10:30:00.000Z"
      }
    ],
    "count": 1
  }
}
```

### **3. List Dictations (Patient View)**
**GET** `/patient/{patient_id}/dictations`

**Status:** Currently returns `501 Not Implemented`

---

## 🧪 Test Cases Included

### **1. Create Dictation Tests**
- ✅ **English Dictation** - Basic medical notes
- ✅ **Tamil Dictation** - Regional language support
- ✅ **Hindi Dictation** - Multi-language support
- ✅ **Long Text** - Comprehensive medical history
- ❌ **Missing Language** - Error handling
- ❌ **No Token** - Authentication error

### **2. List Dictation Tests**
- ✅ **Get All Dictations** - Basic listing
- ✅ **Pagination** - Limit and offset
- ✅ **Language Filter** - Filter by language
- ✅ **Date Range Filter** - Filter by date range
- ❌ **No Token** - Authentication error
- ❌ **Invalid Role** - Authorization error

### **3. Error Scenarios**
- **400 Bad Request** - Missing required fields
- **401 Unauthorized** - Missing or invalid token
- **403 Forbidden** - Insufficient permissions
- **501 Not Implemented** - Patient view (future feature)

---

## 🌍 Multi-Language Support

The API supports multiple languages:

| Language Code | Language | Example |
|---------------|----------|---------|
| `en` | English | "Patient reports feeling better" |
| `ta` | Tamil | "நோயாளி இன்று நன்றாக உணர்கிறார்" |
| `hi` | Hindi | "मरीज़ आज बेहतर महसूस कर रहे हैं" |
| `es` | Spanish | "El paciente se siente mejor hoy" |
| `fr` | French | "Le patient se sent mieux aujourd'hui" |

---

## 📊 Storage Architecture

### **New Storage System:**
- **Collection:** `doctor_v2`
- **Structure:** Dictations stored as array within doctor document
- **Filtering:** By `doctor_id` (from JWT) and `patient_id`

### **Doctor Document Structure:**
```json
{
  "_id": "ObjectId",
  "doctor_id": "DR123",
  "username": "Dr. Smith",
  "email": "dr.smith@example.com",
  "last_dictation_at": "2025-10-22T10:30:00Z",
  "dictations": [
    {
      "dictation_id": "dict_1737542400000",
      "patient_id": "PAT175820015455746A",
      "language": "en",
      "text": "Patient reports feeling better...",
      "source": "doctor_dictation",
      "created_at": "2025-10-22T10:30:00Z",
      "updated_at": "2025-10-22T10:30:00Z"
    }
  ]
}
```

---

## 🔧 Setup Instructions

### **1. Prerequisites**
- Postman installed
- API server running on `http://localhost:8000`
- Valid JWT tokens for doctor and patient

### **2. Environment Setup**
1. Create new environment in Postman
2. Add variables as shown above
3. Set correct values for your setup

### **3. Authentication Setup**
1. Use login endpoints to get JWT tokens
2. Copy tokens to environment variables
3. Tokens will be automatically used in requests

---

## 🚨 Error Codes Reference

| Code | Status | Description | Solution |
|------|--------|-------------|----------|
| 200 | OK | Request successful | - |
| 201 | Created | Dictation created successfully | - |
| 400 | Bad Request | Missing required fields | Check request body |
| 401 | Unauthorized | Missing or invalid token | Login and get valid token |
| 403 | Forbidden | Insufficient permissions | Use correct role token |
| 500 | Internal Server Error | Server error | Check server logs |
| 501 | Not Implemented | Feature not available | Use alternative endpoint |

---

## 📝 Sample Requests

### **Create English Dictation:**
```bash
curl -X POST http://localhost:8000/doctor/patient/PAT175820015455746A/dictations \
  -H "Authorization: Bearer YOUR_DOCTOR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "text": "Patient reports feeling better today. Blood pressure is stable at 120/80."
  }'
```

### **Get All Dictations:**
```bash
curl -X GET http://localhost:8000/doctor/patient/PAT175820015455746A/dictations \
  -H "Authorization: Bearer YOUR_DOCTOR_JWT_TOKEN"
```

### **Get Dictations by Language:**
```bash
curl -X GET "http://localhost:8000/doctor/patient/PAT175820015455746A/dictations?language=en" \
  -H "Authorization: Bearer YOUR_DOCTOR_JWT_TOKEN"
```

---

## 🎉 Features

- ✅ **Multi-language Support** - English, Tamil, Hindi, and more
- ✅ **Doctor-based Storage** - Dictations stored in doctor's document
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Pagination Support** - Limit and offset for large datasets
- ✅ **Date Filtering** - Filter by date range
- ✅ **Language Filtering** - Filter by specific language
- ✅ **Error Handling** - Comprehensive error responses
- ✅ **Input Validation** - Required field validation
- ✅ **Role-based Access** - Doctor and patient roles

---

## 📞 Support

If you encounter any issues:

1. **Check JWT Tokens** - Ensure tokens are valid and not expired
2. **Verify Patient ID** - Use correct patient ID format
3. **Check Server Status** - Ensure API server is running
4. **Review Error Messages** - Check response for specific error details

---

**Collection Version:** 1.0.0  
**API Version:** Doctor Storage System  
**Last Updated:** October 22, 2025  
**Status:** ✅ **Ready for Testing!**
