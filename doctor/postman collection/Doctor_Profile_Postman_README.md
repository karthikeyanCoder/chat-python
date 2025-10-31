# Doctor Profile API Postman Collection

This Postman collection provides comprehensive testing for the Doctor Profile API endpoints, including GET and PUT operations for retrieving and updating doctor profile information.

## 📋 Collection Overview

The collection includes the following main sections:

1. **Authentication** - Doctor login to get access token
2. **Doctor Profile** - GET, PUT, and POST operations for profile management
3. **Health Check** - API server health verification

## 🚀 Quick Start

### Prerequisites
- Postman installed
- Backend server running on `http://localhost:5000`
- Test doctor account credentials

### Import the Collection
1. Open Postman
2. Click "Import" button
3. Select `Doctor_Profile_Postman_Collection.json`
4. The collection will be imported with all requests and examples

## 🔐 Authentication Setup

### Step 1: Doctor Login
1. Run the **"Doctor Login"** request in the Authentication folder
2. This will automatically save the `auth_token` and `doctor_id` to collection variables
3. All subsequent requests will use these variables automatically

**Test Credentials:**
```json
{
  "email": "testdoctor@example.com",
  "password": "testpass123"
}
```

**Expected Response:**
```json
{
  "doctor_id": "D17589491885545840",
  "email": "testdoctor@example.com",
  "message": "Login successful",
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 📊 API Endpoints

### 1. Get Doctor Profile
**Endpoint:** `GET /doctor/profile/{doctor_id}`

**Purpose:** Retrieve doctor profile information

**Headers:**
```
Authorization: Bearer {auth_token}
```

**Example Request:**
```
GET http://localhost:5000/doctor/profile/D17589491885545840
```

**Example Response:**
```json
{
  "success": true,
  "doctor": {
    "doctor_id": "D17589491885545840",
    "username": "testdoctor",
    "email": "testdoctor@example.com",
    "mobile": "9876543210",
    "role": "doctor",
    "first_name": "Dr. John",
    "last_name": "Smith",
    "specialization": "Cardiology",
    "license_number": "MD123456789",
    "experience_years": 10,
    "hospital_name": "City General Hospital",
    "address": "123 Medical Street",
    "city": "New York",
    "state": "NY",
    "pincode": "10001",
    "consultation_fee": 150,
    "profile_url": "https://example.com/doctor-profile",
    "available_timings": {
      "monday": "09:00-17:00",
      "tuesday": "09:00-17:00",
      "wednesday": "09:00-17:00",
      "thursday": "09:00-17:00",
      "friday": "09:00-17:00",
      "saturday": "09:00-13:00",
      "sunday": "closed"
    },
    "languages": ["English", "Spanish"],
    "qualifications": [
      "MBBS - Harvard Medical School",
      "MD Cardiology - Johns Hopkins",
      "Fellowship in Interventional Cardiology"
    ],
    "created_at": "Sat, 27 Sep 2025 10:29:49 GMT",
    "updated_at": "Sat, 27 Sep 2025 17:47:28 GMT"
  }
}
```

### 2. Update Doctor Profile
**Endpoint:** `PUT /doctor/profile/{doctor_id}`

**Purpose:** Update doctor profile information

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {auth_token}
```

**Request Body:**
```json
{
  "first_name": "Dr. John",
  "last_name": "Smith",
  "specialization": "Cardiology",
  "license_number": "MD123456789",
  "experience_years": 10,
  "hospital_name": "City General Hospital",
  "address": "123 Medical Street",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "consultation_fee": 150,
  "profile_url": "https://example.com/doctor-profile",
  "available_timings": {
    "monday": "09:00-17:00",
    "tuesday": "09:00-17:00",
    "wednesday": "09:00-17:00",
    "thursday": "09:00-17:00",
    "friday": "09:00-17:00",
    "saturday": "09:00-13:00",
    "sunday": "closed"
  },
  "languages": ["English", "Spanish"],
  "qualifications": [
    "MBBS - Harvard Medical School",
    "MD Cardiology - Johns Hopkins",
    "Fellowship in Interventional Cardiology"
  ]
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

### 3. Complete Doctor Profile
**Endpoint:** `POST /doctor/complete-profile`

**Purpose:** Complete initial doctor profile setup

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {auth_token}
```

**Request Body:**
```json
{
  "doctor_id": "D17589491885545840",
  "first_name": "Dr. Jane",
  "last_name": "Doe",
  "specialization": "General Medicine",
  "license_number": "MD987654321",
  "experience_years": 5,
  "hospital_name": "Community Health Center",
  "address": "456 Health Avenue",
  "city": "Boston",
  "state": "MA",
  "pincode": "02101",
  "consultation_fee": 120,
  "languages": ["English", "French"],
  "qualifications": [
    "MBBS - Boston University",
    "MD Internal Medicine - Tufts Medical Center"
  ]
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Profile completed successfully"
}
```

## 📝 Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doctor_id` | String | Yes | Unique doctor identifier |
| `first_name` | String | Yes | Doctor's first name |
| `last_name` | String | Yes | Doctor's last name |
| `specialization` | String | Yes | Medical specialization |
| `license_number` | String | Yes | Medical license number |
| `experience_years` | Integer | No | Years of experience |
| `hospital_name` | String | No | Hospital or clinic name |
| `address` | String | No | Street address |
| `city` | String | No | City |
| `state` | String | No | State |
| `pincode` | String | No | ZIP/postal code |
| `consultation_fee` | Integer | No | Consultation fee in currency units |
| `profile_url` | String | No | Profile photo URL |
| `available_timings` | Object | No | Available consultation times |
| `languages` | Array | No | Languages spoken |
| `qualifications` | Array | No | Medical qualifications |

## 🔧 Collection Variables

The collection uses the following variables:

- `base_url`: API server base URL (default: http://localhost:5000)
- `doctor_id`: Doctor ID (auto-populated after login)
- `auth_token`: Authentication token (auto-populated after login)

## 🧪 Testing Scenarios

### Success Scenarios
1. **Valid Login** - Login with correct credentials
2. **Get Profile** - Retrieve existing doctor profile
3. **Update Profile** - Update profile with valid data
4. **Complete Profile** - Complete initial profile setup

### Error Scenarios
1. **Invalid Login** - Login with wrong credentials
2. **Missing Token** - Access protected endpoints without token
3. **Invalid Doctor ID** - Access non-existent doctor profile
4. **Missing Data** - Update profile without required fields

## 🚨 Error Responses

### Common Error Codes

**400 Bad Request**
```json
{
  "error": "No data provided"
}
```

**401 Unauthorized**
```json
{
  "error": "Invalid or missing token"
}
```

**404 Not Found**
```json
{
  "error": "Doctor not found"
}
```

**500 Internal Server Error**
```json
{
  "error": "Server error: Database connection failed"
}
```

## 🔄 Workflow Example

1. **Start Backend Server**
   ```bash
   python app_mvc.py
   ```

2. **Run Health Check**
   - Execute "API Health Check" request
   - Verify server is running

3. **Authenticate**
   - Run "Doctor Login" request
   - Verify token is saved

4. **Get Profile**
   - Run "Get Doctor Profile" request
   - Verify profile data is returned

5. **Update Profile**
   - Modify the request body in "Update Doctor Profile"
   - Run the request
   - Verify success response

6. **Verify Changes**
   - Run "Get Doctor Profile" again
   - Verify changes are reflected

## 📚 Additional Resources

- **Backend API Documentation**: Check `app_mvc.py` for complete endpoint documentation
- **Database Schema**: Check `models/doctor_model.py` for data structure details
- **Controller Logic**: Check `controllers/doctor_controller.py` for business logic

## 🐛 Troubleshooting

### Common Issues

1. **Server Not Running**
   - Ensure backend server is running on port 5000
   - Check server logs for errors

2. **Authentication Failed**
   - Verify test doctor account exists
   - Check credentials in the login request

3. **Profile Not Found**
   - Ensure doctor_id is correct
   - Verify doctor exists in database

4. **Update Failed**
   - Check request body format
   - Verify all required fields are provided

### Debug Steps

1. Check server logs for detailed error messages
2. Verify collection variables are set correctly
3. Test with different doctor IDs
4. Check network connectivity to localhost:5000

## 📞 Support

For issues or questions:
1. Check the backend server logs
2. Verify the API endpoints are working
3. Test with the provided example data
4. Ensure all prerequisites are met

---

**Note**: This collection is designed for development and testing purposes. Update the `base_url` variable for different environments (staging, production).
