# Authentication API Postman Collection

## 📋 Overview
This Postman collection contains all authentication endpoints for the Patient Alert System, including signup, login, OTP verification, and password management.

## 🚀 Setup Instructions

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select the `Authentication_Postman_Collection.json` file
4. The collection will be imported with all endpoints

### 2. Environment Variables
The collection uses these variables (automatically set):

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | Base URL for the API |
| `signup_token` | (auto-set) | JWT token from signup response |
| `reset_token` | (auto-set) | JWT token from password reset |
| `access_token` | (auto-set) | Access token from login |
| `refresh_token` | (auto-set) | Refresh token from login |

### 3. Start Your Flask Server
```bash
python app_mvc.py
```

## 📚 API Endpoints

### 🏥 Health Check
- **GET** `/health` - Check server status

### 👨‍⚕️ Doctor Authentication

#### Doctor Signup
- **POST** `/doctor-signup`
- **Description**: Register a new doctor (automatically sends OTP)
- **Request Body**:
```json
{
    "username": "DrJohnSmith",
    "email": "dr.john.smith@example.com",
    "mobile": "9876543210",
    "password": "SecurePass123!",
    "role": "doctor"
}
```
- **Response**:
```json
{
    "email": "dr.john.smith@example.com",
    "message": "Please check your email for OTP verification.",
    "signup_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "status": "otp_sent"
}
```

#### Doctor Send OTP (Alternative)
- **POST** `/doctor-send-otp`
- **Description**: Send OTP to doctor email (alternative endpoint)
- **Request Body**:
```json
{
    "email": "dr.john.smith@example.com",
    "purpose": "signup"
}
```

#### Doctor Verify OTP
- **POST** `/doctor-verify-otp`
- **Description**: Verify OTP for doctor signup completion
- **Request Body**:
```json
{
    "email": "dr.john.smith@example.com",
    "otp": "123456",
    "jwt_token": "{{signup_token}}",
    "role": "doctor"
}
```

#### Doctor Login
- **POST** `/doctor-login`
- **Description**: Login for existing doctor account
- **Request Body**:
```json
{
    "email": "dr.john.smith@example.com",
    "password": "SecurePass123!",
    "role": "doctor"
}
```

### 👤 Patient Authentication

#### Patient Signup
- **POST** `/patient/signup`
- **Description**: Register a new patient
- **Request Body**:
```json
{
    "username": "PatientUser",
    "email": "patient@example.com",
    "mobile": "9876543211",
    "password": "PatientPass123!",
    "role": "patient"
}
```

#### Patient Verify OTP
- **POST** `/patient/verify-otp`
- **Description**: Verify OTP for patient signup completion
- **Request Body**:
```json
{
    "email": "patient@example.com",
    "otp": "123456",
    "role": "patient"
}
```

### 🔐 Password Management

#### Doctor Forgot Password
- **POST** `/doctor-forgot-password`
- **Description**: Send OTP for doctor password reset
- **Request Body**:
```json
{
    "email": "dr.john.smith@example.com"
}
```
- **Success Response**:
```json
{
    "success": true,
    "message": "OTP sent to your email for password reset",
    "email": "dr.john.smith@example.com",
    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "otp": "123456"
}
```
- **Error Response** (Doctor not found):
```json
{
    "error": "Doctor not found"
}
```

#### Doctor Reset Password
- **POST** `/doctor-reset-password`
- **Description**: Reset doctor password using OTP verification
- **Request Body**:
```json
{
    "email": "dr.john.smith@example.com",
    "otp": "123456",
    "jwt_token": "{{reset_token}}",
    "new_password": "NewSecurePass123!"
}
```
- **Success Response**:
```json
{
    "success": true,
    "message": "Password reset successfully"
}
```
- **Error Response** (Invalid OTP):
```json
{
    "error": "Invalid OTP"
}
```

#### Generic Reset Password
- **POST** `/reset-password`
- **Description**: Generic password reset endpoint
- **Request Body**:
```json
{
    "email": "user@example.com",
    "otp": "123456",
    "jwt_token": "{{reset_token}}",
    "new_password": "NewSecurePass123!",
    "role": "doctor"
}
```
- **Success Response**:
```json
{
    "success": true,
    "message": "Password reset successfully"
}
```
- **Error Response** (Missing fields):
```json
{
    "error": "Email, new password, OTP, and JWT token are required"
}
```

### 👤 Profile Management

#### Get Doctor Profile Fields
- **GET** `/doctor-profile-fields`
- **Headers**: `Authorization: Bearer {{access_token}}`
- **Description**: Get available fields for doctor profile completion
- **Response**:
```json
{
    "message": "Available doctor profile fields",
    "profile_fields": {
        "address_info": {
            "address": {
                "description": "Practice address",
                "required": false,
                "type": "string"
            },
            "city": {
                "description": "City",
                "required": false,
                "type": "string"
            },
            "pincode": {
                "description": "Pincode",
                "required": false,
                "type": "string"
            },
            "state": {
                "description": "State",
                "required": false,
                "type": "string"
            }
        },
        "personal_info": {
            "email": {
                "description": "Doctor email address",
                "required": true,
                "type": "email"
            },
            "first_name": {
                "description": "Doctor first name",
                "required": true,
                "type": "string"
            },
            "last_name": {
                "description": "Doctor last name",
                "required": true,
                "type": "string"
            },
            "mobile": {
                "description": "Doctor mobile number",
                "required": true,
                "type": "string"
            }
        },
        "practice_info": {
            "available_timings": {
                "description": "Available consultation timings",
                "required": false,
                "type": "object"
            },
            "consultation_fee": {
                "description": "Consultation fee",
                "required": false,
                "type": "number"
            },
            "hospital_name": {
                "description": "Hospital or clinic name",
                "required": false,
                "type": "string"
            },
            "languages": {
                "description": "Languages spoken",
                "required": false,
                "type": "array"
            }
        },
        "professional_info": {
            "experience_years": {
                "description": "Years of experience",
                "required": true,
                "type": "number"
            },
            "license_number": {
                "description": "Medical license number",
                "required": true,
                "type": "string"
            },
            "qualifications": {
                "description": "List of qualifications",
                "required": false,
                "type": "array"
            },
            "specialization": {
                "description": "Medical specialization",
                "required": true,
                "type": "string"
            }
        }
    },
    "success": true
}
```

#### Complete Doctor Profile
- **POST** `/doctor-complete-profile`
- **Headers**: `Authorization: Bearer {{access_token}}`
- **Description**: Complete doctor profile with additional information
- **Request Body**:
```json
{
    "specialization": "Cardiology",
    "experience_years": 10,
    "qualification": "MD, DM Cardiology",
    "hospital_affiliation": "City General Hospital",
    "license_number": "MED123456",
    "consultation_fee": 500,
    "available_hours": "9:00 AM - 5:00 PM",
    "languages": ["English", "Hindi"],
    "bio": "Experienced cardiologist with 10+ years of practice"
}
```

#### Generic Complete Profile
- **POST** `/complete-profile`
- **Headers**: `Authorization: Bearer {{access_token}}`
- **Description**: Generic profile completion endpoint
- **Request Body**:
```json
{
    "role": "doctor",
    "specialization": "Cardiology",
    "experience_years": 10,
    "qualification": "MD, DM Cardiology"
}
```

### 🛠️ Utility Endpoints

#### Resend OTP
- **POST** `/resend-otp`
- **Description**: Resend OTP for verification
- **Request Body**:
```json
{
    "email": "dr.john.smith@example.com",
    "role": "doctor"
}
```

#### Generic Login
- **POST** `/login`
- **Description**: Generic login endpoint for both doctors and patients
- **Request Body**:
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "role": "doctor"
}
```

#### Debug Test Login
- **POST** `/debug/test-login`
- **Description**: Debug endpoint for testing login functionality
- **Request Body**:
```json
{
    "email": "test@example.com",
    "password": "testpass",
    "role": "doctor"
}
```

## 🔄 Complete Authentication Flow

### Doctor Signup Flow:
1. **POST** `/doctor-signup` → Get `signup_token` and OTP via email
2. **POST** `/doctor-verify-otp` → Verify OTP and complete signup
3. **POST** `/doctor-complete-profile` → Complete profile (optional)

### Doctor Login Flow:
1. **POST** `/doctor-login` → Get `access_token` and `refresh_token`
2. Use `access_token` in Authorization header for protected endpoints

### Password Reset Flow:
1. **POST** `/doctor-forgot-password` → Get OTP and JWT token via email
2. **POST** `/doctor-reset-password` → Reset password with OTP and JWT token

### Complete Forgot Password Flow:
1. **POST** `/doctor-forgot-password`
   - **Input**: `{"email": "doctor@example.com"}`
   - **Output**: `{"success": true, "message": "OTP sent...", "jwt_token": "...", "otp": "123456"}`
2. **POST** `/doctor-reset-password`
   - **Input**: `{"email": "doctor@example.com", "otp": "123456", "jwt_token": "...", "new_password": "NewPass123!"}`
   - **Output**: `{"success": true, "message": "Password reset successfully"}`

## 📧 Email Configuration

Make sure your email service is configured in the backend:
- Update email credentials in environment variables
- Test email sending with the health check endpoint

## 🧪 Testing Tips

1. **Start with Health Check**: Always test `/health` first
2. **Use Test Data**: Use the provided sample data in requests
3. **Check Responses**: Look for `signup_token`, `access_token` in responses
4. **Environment Variables**: Tokens are automatically stored in variables
5. **Error Handling**: Check for error messages in responses

## 🔧 Troubleshooting

### Common Issues:
1. **Connection Refused**: Make sure Flask server is running on port 5000
2. **404 Errors**: Check endpoint URLs and HTTP methods
3. **Email Not Sent**: Verify email service configuration
4. **Token Issues**: Check JWT secret key configuration

### Debug Steps:
1. Check server logs for detailed error messages
2. Verify database connection
3. Test email service independently
4. Check environment variables

## 📝 Notes

- All timestamps are in UTC
- JWT tokens expire in 10 minutes for OTP verification
- Access tokens have longer expiration (configurable)
- Email sending may fail but OTP is still generated
- Use HTTPS in production environment

---

**Happy Testing! 🚀**
