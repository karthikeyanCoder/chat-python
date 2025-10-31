# Profile URL Input and Output - Postman Collection

## 📋 Overview

This Postman collection provides comprehensive testing for the **Profile URL Input and Output** functionality in the Doctor Profile Management system. It includes all necessary endpoints for testing profile URL validation, input, output, and error handling.

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click **Import** button
3. Select `Profile_URL_Postman_Collection.json`
4. The collection will be imported with all requests and variables

### 2. Set Up Environment Variables
The collection uses these variables (automatically set during login):
- `base_url`: `http://localhost:5000`
- `auth_token`: Auto-populated after doctor login
- `doctor_id`: Auto-populated after doctor login
- `profile_url`: `https://www.drramya.com/profile`

### 3. Run Authentication
1. Go to **Authentication** folder
2. Run **Doctor Login** request
3. The `auth_token` and `doctor_id` will be automatically saved

## 📁 Collection Structure

### 🔐 Authentication
- **Doctor Login**: Authenticate and get JWT token
  - Auto-saves `auth_token` and `doctor_id` variables
  - Required for all subsequent requests

### 🔗 Profile URL Management
- **Get Doctor Profile**: Check current profile URL
- **Update Profile with Valid URL**: Set a valid profile URL
- **Update Profile with Different URL**: Change to a different URL
- **Update Profile with Empty URL**: Clear the profile URL

### ✅ URL Validation Tests
- **Test Valid HTTPS URL**: `https://www.example.com/doctor-profile`
- **Test Valid HTTP URL**: `http://www.example.com/doctor-profile`
- **Test Invalid URL Format**: `invalid-url-format`
- **Test URL with Query Parameters**: `https://www.example.com/doctor-profile?ref=medical-portal&id=123`
- **Test URL with Fragment**: `https://www.example.com/doctor-profile#contact-section`

### 📤 Profile URL Output Tests
- **Get Profile with URL Display**: Verify profile URL in response
- **Get All Doctors with Profile URLs**: List view with profile URLs

### ❌ Error Handling Tests
- **Update Profile without Authentication**: Test unauthorized access
- **Update Non-existent Doctor Profile**: Test invalid doctor ID
- **Update Profile with Missing Required Fields**: Test validation

### 📱 Flutter App Integration Tests
- **Test Profile URL Input Validation**: Flutter app payload format
- **Test Profile URL Output for Flutter Display**: Response format for Flutter

## 🧪 Test Scenarios

### 1. Basic Profile URL Operations

#### ✅ Valid URL Input
```json
{
  "first_name": "Dr. Ramya",
  "last_name": "Yashva",
  "specialization": "General Medicine",
  "profile_url": "https://www.drramya.com/profile"
}
```

#### ✅ URL Output Verification
```json
{
  "success": true,
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "profile_url": "https://www.drramya.com/profile",
    "updated_at": "2025-01-26T16:00:00Z"
  }
}
```

### 2. URL Validation Tests

| Test Case | URL Input | Expected Result |
|-----------|-----------|-----------------|
| Valid HTTPS | `https://www.example.com/profile` | ✅ Accepted |
| Valid HTTP | `http://www.example.com/profile` | ✅ Accepted |
| Invalid Format | `invalid-url-format` | ⚠️ Accepted by backend, validated by Flutter |
| Empty URL | `""` | ✅ Clears profile URL |
| Query Parameters | `https://example.com/profile?id=123` | ✅ Accepted |
| Fragment | `https://example.com/profile#section` | ✅ Accepted |

### 3. Error Handling

| Scenario | Expected Status | Expected Response |
|----------|----------------|-------------------|
| No Authentication | 401 | `{"error": "Authentication required"}` |
| Invalid Doctor ID | 404 | `{"error": "Doctor not found"}` |
| Missing Required Fields | 400 | `{"error": "Required fields missing"}` |

## 🔧 API Endpoints

### Profile Management
- `GET /doctor/profile/{doctor_id}` - Get doctor profile with URL
- `PUT /doctor/profile/{doctor_id}` - Update doctor profile with URL

### Request Headers
```http
Content-Type: application/json
Authorization: Bearer {auth_token}
```

### Response Format
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "profile_url": "https://www.drramya.com/profile",
    "updated_at": "2025-01-26T16:00:00Z"
  }
}
```

## 📱 Flutter App Integration

### Input Validation (Flutter Side)
```dart
validator: (value) {
  if (value != null && value.isNotEmpty) {
    if (!Uri.tryParse(value)?.hasAbsolutePath ?? true) {
      return 'Please enter a valid URL';
    }
  }
  return null;
}
```

### API Service Call
```dart
final response = await apiService.updateDoctorProfile(
  doctorId: authProvider.patientId!,
  firstName: _firstNameController.text.trim(),
  lastName: _lastNameController.text.trim(),
  // ... other fields
  profileUrl: _profileUrlController.text.trim(),
);
```

### Profile Display (Flutter Side)
```dart
if (_profileData!['profile_url'] != null && 
    _profileData!['profile_url'].isNotEmpty) {
  GestureDetector(
    onTap: () => _launchProfileURL(_profileData!['profile_url']),
    child: Container(
      child: Row(
        children: [
          Icon(Icons.link),
          Text('View Profile'),
        ],
      ),
    ),
  ),
}
```

## 🚨 Common Issues & Solutions

### 1. Authentication Token Expired
**Error**: `401 Unauthorized`
**Solution**: Re-run the "Doctor Login" request to get a fresh token

### 2. Invalid Doctor ID
**Error**: `404 Not Found`
**Solution**: Check that `doctor_id` variable is set correctly after login

### 3. URL Validation Fails
**Error**: Flutter validation error
**Solution**: Ensure URL includes protocol (http:// or https://)

### 4. Profile URL Not Displayed
**Issue**: URL not showing in Flutter app
**Solution**: Check that `profile_url` field is included in API response

## 📊 Test Results Summary

### ✅ Successful Tests
- Profile URL input validation
- Profile URL output display
- URL format validation
- Authentication handling
- Error response handling

### ⚠️ Notes
- Backend accepts any string as profile_url (validation is on Flutter side)
- Empty string clears the profile URL
- URL validation happens in Flutter app, not backend

## 🔄 Running the Collection

### Manual Testing
1. Run requests individually in Postman
2. Check response status codes and data
3. Verify profile URL is saved and retrieved correctly

### Automated Testing
1. Use Postman Collection Runner
2. Select the collection
3. Run all requests in sequence
4. Review test results

### Newman CLI Testing
```bash
newman run Profile_URL_Postman_Collection.json \
  --environment your-environment.json \
  --reporters cli,html \
  --reporter-html-export report.html
```

## 📝 Sample Test Data

### Valid Profile URLs
- `https://www.drramya.com/profile`
- `https://www.linkedin.com/in/dr-ramya-yashva`
- `https://www.example.com/doctor-profile?ref=medical-portal`
- `https://www.example.com/doctor-profile#contact-section`

### Test Doctor Data
```json
{
  "first_name": "Dr. Ramya",
  "last_name": "Yashva",
  "specialization": "General Medicine",
  "license_number": "MED123456",
  "experience_years": 5,
  "hospital_name": "City General Hospital",
  "address": "123 Medical Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "consultation_fee": 500,
  "profile_url": "https://www.drramya.com/profile"
}
```

## 🎯 Next Steps

1. **Import the collection** into Postman
2. **Run the authentication** request first
3. **Test profile URL input** with various URL formats
4. **Verify profile URL output** in responses
5. **Test error scenarios** for comprehensive coverage
6. **Integrate with Flutter app** testing

---

**📞 Support**: If you encounter any issues, check the error responses and ensure the backend server is running on `http://localhost:5000`.

## 📋 Overview

This Postman collection provides comprehensive testing for the **Profile URL Input and Output** functionality in the Doctor Profile Management system. It includes all necessary endpoints for testing profile URL validation, input, output, and error handling.

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click **Import** button
3. Select `Profile_URL_Postman_Collection.json`
4. The collection will be imported with all requests and variables

### 2. Set Up Environment Variables
The collection uses these variables (automatically set during login):
- `base_url`: `http://localhost:5000`
- `auth_token`: Auto-populated after doctor login
- `doctor_id`: Auto-populated after doctor login
- `profile_url`: `https://www.drramya.com/profile`

### 3. Run Authentication
1. Go to **Authentication** folder
2. Run **Doctor Login** request
3. The `auth_token` and `doctor_id` will be automatically saved

## 📁 Collection Structure

### 🔐 Authentication
- **Doctor Login**: Authenticate and get JWT token
  - Auto-saves `auth_token` and `doctor_id` variables
  - Required for all subsequent requests

### 🔗 Profile URL Management
- **Get Doctor Profile**: Check current profile URL
- **Update Profile with Valid URL**: Set a valid profile URL
- **Update Profile with Different URL**: Change to a different URL
- **Update Profile with Empty URL**: Clear the profile URL

### ✅ URL Validation Tests
- **Test Valid HTTPS URL**: `https://www.example.com/doctor-profile`
- **Test Valid HTTP URL**: `http://www.example.com/doctor-profile`
- **Test Invalid URL Format**: `invalid-url-format`
- **Test URL with Query Parameters**: `https://www.example.com/doctor-profile?ref=medical-portal&id=123`
- **Test URL with Fragment**: `https://www.example.com/doctor-profile#contact-section`

### 📤 Profile URL Output Tests
- **Get Profile with URL Display**: Verify profile URL in response
- **Get All Doctors with Profile URLs**: List view with profile URLs

### ❌ Error Handling Tests
- **Update Profile without Authentication**: Test unauthorized access
- **Update Non-existent Doctor Profile**: Test invalid doctor ID
- **Update Profile with Missing Required Fields**: Test validation

### 📱 Flutter App Integration Tests
- **Test Profile URL Input Validation**: Flutter app payload format
- **Test Profile URL Output for Flutter Display**: Response format for Flutter

## 🧪 Test Scenarios

### 1. Basic Profile URL Operations

#### ✅ Valid URL Input
```json
{
  "first_name": "Dr. Ramya",
  "last_name": "Yashva",
  "specialization": "General Medicine",
  "profile_url": "https://www.drramya.com/profile"
}
```

#### ✅ URL Output Verification
```json
{
  "success": true,
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "profile_url": "https://www.drramya.com/profile",
    "updated_at": "2025-01-26T16:00:00Z"
  }
}
```

### 2. URL Validation Tests

| Test Case | URL Input | Expected Result |
|-----------|-----------|-----------------|
| Valid HTTPS | `https://www.example.com/profile` | ✅ Accepted |
| Valid HTTP | `http://www.example.com/profile` | ✅ Accepted |
| Invalid Format | `invalid-url-format` | ⚠️ Accepted by backend, validated by Flutter |
| Empty URL | `""` | ✅ Clears profile URL |
| Query Parameters | `https://example.com/profile?id=123` | ✅ Accepted |
| Fragment | `https://example.com/profile#section` | ✅ Accepted |

### 3. Error Handling

| Scenario | Expected Status | Expected Response |
|----------|----------------|-------------------|
| No Authentication | 401 | `{"error": "Authentication required"}` |
| Invalid Doctor ID | 404 | `{"error": "Doctor not found"}` |
| Missing Required Fields | 400 | `{"error": "Required fields missing"}` |

## 🔧 API Endpoints

### Profile Management
- `GET /doctor/profile/{doctor_id}` - Get doctor profile with URL
- `PUT /doctor/profile/{doctor_id}` - Update doctor profile with URL

### Request Headers
```http
Content-Type: application/json
Authorization: Bearer {auth_token}
```

### Response Format
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "profile_url": "https://www.drramya.com/profile",
    "updated_at": "2025-01-26T16:00:00Z"
  }
}
```

## 📱 Flutter App Integration

### Input Validation (Flutter Side)
```dart
validator: (value) {
  if (value != null && value.isNotEmpty) {
    if (!Uri.tryParse(value)?.hasAbsolutePath ?? true) {
      return 'Please enter a valid URL';
    }
  }
  return null;
}
```

### API Service Call
```dart
final response = await apiService.updateDoctorProfile(
  doctorId: authProvider.patientId!,
  firstName: _firstNameController.text.trim(),
  lastName: _lastNameController.text.trim(),
  // ... other fields
  profileUrl: _profileUrlController.text.trim(),
);
```

### Profile Display (Flutter Side)
```dart
if (_profileData!['profile_url'] != null && 
    _profileData!['profile_url'].isNotEmpty) {
  GestureDetector(
    onTap: () => _launchProfileURL(_profileData!['profile_url']),
    child: Container(
      child: Row(
        children: [
          Icon(Icons.link),
          Text('View Profile'),
        ],
      ),
    ),
  ),
}
```

## 🚨 Common Issues & Solutions

### 1. Authentication Token Expired
**Error**: `401 Unauthorized`
**Solution**: Re-run the "Doctor Login" request to get a fresh token

### 2. Invalid Doctor ID
**Error**: `404 Not Found`
**Solution**: Check that `doctor_id` variable is set correctly after login

### 3. URL Validation Fails
**Error**: Flutter validation error
**Solution**: Ensure URL includes protocol (http:// or https://)

### 4. Profile URL Not Displayed
**Issue**: URL not showing in Flutter app
**Solution**: Check that `profile_url` field is included in API response

## 📊 Test Results Summary

### ✅ Successful Tests
- Profile URL input validation
- Profile URL output display
- URL format validation
- Authentication handling
- Error response handling

### ⚠️ Notes
- Backend accepts any string as profile_url (validation is on Flutter side)
- Empty string clears the profile URL
- URL validation happens in Flutter app, not backend

## 🔄 Running the Collection

### Manual Testing
1. Run requests individually in Postman
2. Check response status codes and data
3. Verify profile URL is saved and retrieved correctly

### Automated Testing
1. Use Postman Collection Runner
2. Select the collection
3. Run all requests in sequence
4. Review test results

### Newman CLI Testing
```bash
newman run Profile_URL_Postman_Collection.json \
  --environment your-environment.json \
  --reporters cli,html \
  --reporter-html-export report.html
```

## 📝 Sample Test Data

### Valid Profile URLs
- `https://www.drramya.com/profile`
- `https://www.linkedin.com/in/dr-ramya-yashva`
- `https://www.example.com/doctor-profile?ref=medical-portal`
- `https://www.example.com/doctor-profile#contact-section`

### Test Doctor Data
```json
{
  "first_name": "Dr. Ramya",
  "last_name": "Yashva",
  "specialization": "General Medicine",
  "license_number": "MED123456",
  "experience_years": 5,
  "hospital_name": "City General Hospital",
  "address": "123 Medical Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "consultation_fee": 500,
  "profile_url": "https://www.drramya.com/profile"
}
```

## 🎯 Next Steps

1. **Import the collection** into Postman
2. **Run the authentication** request first
3. **Test profile URL input** with various URL formats
4. **Verify profile URL output** in responses
5. **Test error scenarios** for comprehensive coverage
6. **Integrate with Flutter app** testing

---

**📞 Support**: If you encounter any issues, check the error responses and ensure the backend server is running on `http://localhost:5000`.

## 📋 Overview

This Postman collection provides comprehensive testing for the **Profile URL Input and Output** functionality in the Doctor Profile Management system. It includes all necessary endpoints for testing profile URL validation, input, output, and error handling.

## 🚀 Quick Start

### 1. Import Collection
1. Open Postman
2. Click **Import** button
3. Select `Profile_URL_Postman_Collection.json`
4. The collection will be imported with all requests and variables

### 2. Set Up Environment Variables
The collection uses these variables (automatically set during login):
- `base_url`: `http://localhost:5000`
- `auth_token`: Auto-populated after doctor login
- `doctor_id`: Auto-populated after doctor login
- `profile_url`: `https://www.drramya.com/profile`

### 3. Run Authentication
1. Go to **Authentication** folder
2. Run **Doctor Login** request
3. The `auth_token` and `doctor_id` will be automatically saved

## 📁 Collection Structure

### 🔐 Authentication
- **Doctor Login**: Authenticate and get JWT token
  - Auto-saves `auth_token` and `doctor_id` variables
  - Required for all subsequent requests

### 🔗 Profile URL Management
- **Get Doctor Profile**: Check current profile URL
- **Update Profile with Valid URL**: Set a valid profile URL
- **Update Profile with Different URL**: Change to a different URL
- **Update Profile with Empty URL**: Clear the profile URL

### ✅ URL Validation Tests
- **Test Valid HTTPS URL**: `https://www.example.com/doctor-profile`
- **Test Valid HTTP URL**: `http://www.example.com/doctor-profile`
- **Test Invalid URL Format**: `invalid-url-format`
- **Test URL with Query Parameters**: `https://www.example.com/doctor-profile?ref=medical-portal&id=123`
- **Test URL with Fragment**: `https://www.example.com/doctor-profile#contact-section`

### 📤 Profile URL Output Tests
- **Get Profile with URL Display**: Verify profile URL in response
- **Get All Doctors with Profile URLs**: List view with profile URLs

### ❌ Error Handling Tests
- **Update Profile without Authentication**: Test unauthorized access
- **Update Non-existent Doctor Profile**: Test invalid doctor ID
- **Update Profile with Missing Required Fields**: Test validation

### 📱 Flutter App Integration Tests
- **Test Profile URL Input Validation**: Flutter app payload format
- **Test Profile URL Output for Flutter Display**: Response format for Flutter

## 🧪 Test Scenarios

### 1. Basic Profile URL Operations

#### ✅ Valid URL Input
```json
{
  "first_name": "Dr. Ramya",
  "last_name": "Yashva",
  "specialization": "General Medicine",
  "profile_url": "https://www.drramya.com/profile"
}
```

#### ✅ URL Output Verification
```json
{
  "success": true,
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "profile_url": "https://www.drramya.com/profile",
    "updated_at": "2025-01-26T16:00:00Z"
  }
}
```

### 2. URL Validation Tests

| Test Case | URL Input | Expected Result |
|-----------|-----------|-----------------|
| Valid HTTPS | `https://www.example.com/profile` | ✅ Accepted |
| Valid HTTP | `http://www.example.com/profile` | ✅ Accepted |
| Invalid Format | `invalid-url-format` | ⚠️ Accepted by backend, validated by Flutter |
| Empty URL | `""` | ✅ Clears profile URL |
| Query Parameters | `https://example.com/profile?id=123` | ✅ Accepted |
| Fragment | `https://example.com/profile#section` | ✅ Accepted |

### 3. Error Handling

| Scenario | Expected Status | Expected Response |
|----------|----------------|-------------------|
| No Authentication | 401 | `{"error": "Authentication required"}` |
| Invalid Doctor ID | 404 | `{"error": "Doctor not found"}` |
| Missing Required Fields | 400 | `{"error": "Required fields missing"}` |

## 🔧 API Endpoints

### Profile Management
- `GET /doctor/profile/{doctor_id}` - Get doctor profile with URL
- `PUT /doctor/profile/{doctor_id}` - Update doctor profile with URL

### Request Headers
```http
Content-Type: application/json
Authorization: Bearer {auth_token}
```

### Response Format
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "doctor": {
    "doctor_id": "D17587987732214",
    "first_name": "Dr. Ramya",
    "last_name": "Yashva",
    "profile_url": "https://www.drramya.com/profile",
    "updated_at": "2025-01-26T16:00:00Z"
  }
}
```

## 📱 Flutter App Integration

### Input Validation (Flutter Side)
```dart
validator: (value) {
  if (value != null && value.isNotEmpty) {
    if (!Uri.tryParse(value)?.hasAbsolutePath ?? true) {
      return 'Please enter a valid URL';
    }
  }
  return null;
}
```

### API Service Call
```dart
final response = await apiService.updateDoctorProfile(
  doctorId: authProvider.patientId!,
  firstName: _firstNameController.text.trim(),
  lastName: _lastNameController.text.trim(),
  // ... other fields
  profileUrl: _profileUrlController.text.trim(),
);
```

### Profile Display (Flutter Side)
```dart
if (_profileData!['profile_url'] != null && 
    _profileData!['profile_url'].isNotEmpty) {
  GestureDetector(
    onTap: () => _launchProfileURL(_profileData!['profile_url']),
    child: Container(
      child: Row(
        children: [
          Icon(Icons.link),
          Text('View Profile'),
        ],
      ),
    ),
  ),
}
```

## 🚨 Common Issues & Solutions

### 1. Authentication Token Expired
**Error**: `401 Unauthorized`
**Solution**: Re-run the "Doctor Login" request to get a fresh token

### 2. Invalid Doctor ID
**Error**: `404 Not Found`
**Solution**: Check that `doctor_id` variable is set correctly after login

### 3. URL Validation Fails
**Error**: Flutter validation error
**Solution**: Ensure URL includes protocol (http:// or https://)

### 4. Profile URL Not Displayed
**Issue**: URL not showing in Flutter app
**Solution**: Check that `profile_url` field is included in API response

## 📊 Test Results Summary

### ✅ Successful Tests
- Profile URL input validation
- Profile URL output display
- URL format validation
- Authentication handling
- Error response handling

### ⚠️ Notes
- Backend accepts any string as profile_url (validation is on Flutter side)
- Empty string clears the profile URL
- URL validation happens in Flutter app, not backend

## 🔄 Running the Collection

### Manual Testing
1. Run requests individually in Postman
2. Check response status codes and data
3. Verify profile URL is saved and retrieved correctly

### Automated Testing
1. Use Postman Collection Runner
2. Select the collection
3. Run all requests in sequence
4. Review test results

### Newman CLI Testing
```bash
newman run Profile_URL_Postman_Collection.json \
  --environment your-environment.json \
  --reporters cli,html \
  --reporter-html-export report.html
```

## 📝 Sample Test Data

### Valid Profile URLs
- `https://www.drramya.com/profile`
- `https://www.linkedin.com/in/dr-ramya-yashva`
- `https://www.example.com/doctor-profile?ref=medical-portal`
- `https://www.example.com/doctor-profile#contact-section`

### Test Doctor Data
```json
{
  "first_name": "Dr. Ramya",
  "last_name": "Yashva",
  "specialization": "General Medicine",
  "license_number": "MED123456",
  "experience_years": 5,
  "hospital_name": "City General Hospital",
  "address": "123 Medical Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "consultation_fee": 500,
  "profile_url": "https://www.drramya.com/profile"
}
```

## 🎯 Next Steps

1. **Import the collection** into Postman
2. **Run the authentication** request first
3. **Test profile URL input** with various URL formats
4. **Verify profile URL output** in responses
5. **Test error scenarios** for comprehensive coverage
6. **Integrate with Flutter app** testing

---

**📞 Support**: If you encounter any issues, check the error responses and ensure the backend server is running on `http://localhost:5000`.
