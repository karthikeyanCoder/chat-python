# Patient Profile Requirements - Complete Profile Page

## Overview
This document outlines the essential fields and structure required for a complete patient profile page in the Pregnancy AI Python Backend application.

## Essential Fields for Patient Complete Profile Page

### 1. Core Personal Information (Required)
```json
{
  "first_name": "Jane",           // ✅ REQUIRED
  "last_name": "Smith",           // ✅ REQUIRED  
  "date_of_birth": "1990-05-15",  // ✅ REQUIRED
  "blood_type": "O+",            // ✅ REQUIRED
  "gender": "Female"             // ✅ REQUIRED
}
```

### 2. Contact Information (Important)
```json
{
  "email": "jane.smith@email.com",     // ✅ REQUIRED (for login)
  "mobile": "+1234567890",             // ✅ REQUIRED (for notifications)
  "emergency_contact": "+1987654321",  // ✅ REQUIRED (safety)
  "address": "123 Main St, Cityville, State 12345"  // ✅ REQUIRED (location)
}
```

### 3. Physical Health Data (Important)
```json
{
  "height": 165.0,    // ✅ REQUIRED (for BMI calculations)
  "weight": 62.0      // ✅ REQUIRED (for BMI calculations)
}
```

### 4. Pregnancy-Specific Information (Critical for this app)
```json
{
  "is_pregnant": true,                    // ✅ REQUIRED
  "pregnancy_status": "active",           // ✅ REQUIRED
  "pregnancy_week": 24,                   // ✅ REQUIRED
  "last_period_date": "2024-01-15",       // ✅ REQUIRED (for due date calculation)
  "expected_delivery_date": "2024-10-22"  // ✅ REQUIRED (calculated field)
}
```

### 5. Medical Information (Important for care)
```json
{
  "medical_conditions": [],  // ✅ REQUIRED (can be empty array)
  "allergies": [],           // ✅ REQUIRED (can be empty array)
  "current_medications": []  // ✅ REQUIRED (can be empty array)
}
```

## Complete Patient Profile Form Structure

### Section 1: Basic Information
- **First Name** *(Required)*
- **Last Name** *(Required)*
- **Date of Birth** *(Required)*
- **Gender** *(Required)* - Dropdown: Male/Female/Other
- **Blood Type** *(Required)* - Dropdown: A+, A-, B+, AB+, AB-, O+, O-

### Section 2: Contact Details
- **Email Address** *(Required)* - Already from signup
- **Mobile Number** *(Required)*
- **Emergency Contact** *(Required)*
- **Address** *(Required)*

### Section 3: Physical Measurements
- **Height** *(Required)* - in cm/inches
- **Weight** *(Required)* - in kg/lbs

### Section 4: Pregnancy Information
- **Are you currently pregnant?** *(Required)* - Yes/No
- **Pregnancy Status** *(Required)* - Active/Planning/Postpartum
- **Last Menstrual Period Date** *(Required)* - Date picker
- **Expected Delivery Date** *(Auto-calculated)* - Read-only field

### Section 5: Medical History
- **Medical Conditions** *(Required)* - Multi-select or text area
- **Allergies** *(Required)* - Multi-select or text area  
- **Current Medications** *(Required)* - Multi-select or text area

## Optional but Recommended Fields

### Section 6: Additional Information
```json
{
  "emergency_contact_name": "John Smith",           // Optional but recommended
  "emergency_contact_relationship": "Spouse",       // Optional but recommended
  "city": "Cityville",                              // Optional (extracted from address)
  "state": "State",                                 // Optional (extracted from address)
  "zip_code": "12345"                               // Optional (extracted from address)
}
```

## Profile Completion Validation Logic

```javascript
// Required fields validation
const requiredFields = [
  'first_name', 'last_name', 'date_of_birth', 'blood_type', 'gender',
  'email', 'mobile', 'emergency_contact', 'address',
  'height', 'weight',
  'is_pregnant', 'pregnancy_status', 'last_period_date',
  'medical_conditions', 'allergies', 'current_medications'
];

// Check if profile is complete
function isProfileComplete(patientData) {
  return requiredFields.every(field => {
    const value = patientData[field];
    if (Array.isArray(value)) {
      return value.length >= 0; // Arrays can be empty
    }
    return value !== null && value !== undefined && value !== '';
  });
}
```

## UI/UX Recommendations for Complete Profile Page

### Progressive Form Design
1. **Step 1**: Basic Information (Name, DOB, Gender, Blood Type)
2. **Step 2**: Contact & Address
3. **Step 3**: Physical Measurements
4. **Step 4**: Pregnancy Information
5. **Step 5**: Medical History

### Field Priority Indicators
- 🔴 **Critical**: Core personal info + pregnancy data
- 🟡 **Important**: Contact info + physical measurements
- 🟢 **Optional**: Additional emergency contact details

### Smart Defaults & Auto-calculations
- **Expected Delivery Date**: Auto-calculate from LMP + 280 days
- **Pregnancy Week**: Auto-calculate from LMP
- **BMI**: Auto-calculate from height/weight
- **Age**: Auto-calculate from date of birth

### Validation Messages
```javascript
const validationMessages = {
  'first_name': 'First name is required',
  'last_name': 'Last name is required',
  'date_of_birth': 'Date of birth is required',
  'blood_type': 'Blood type is required for medical records',
  'mobile': 'Mobile number is required for emergency notifications',
  'emergency_contact': 'Emergency contact is required for safety',
  'height': 'Height is required for BMI calculations',
  'weight': 'Weight is required for BMI calculations',
  'last_period_date': 'Last menstrual period date is required for pregnancy tracking'
};
```

## API Integration Points

### Complete Profile Endpoint
```http
POST /complete-profile
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1990-05-15",
  "blood_type": "O+",
  "gender": "Female",
  "height": 165.0,
  "weight": 62.0,
  "emergency_contact": "+1987654321",
  "address": "123 Main St, Cityville, State 12345",
  "is_pregnant": true,
  "pregnancy_status": "active",
  "last_period_date": "2024-01-15",
  "medical_conditions": [],
  "allergies": [],
  "current_medications": []
}
```

### Edit Profile Endpoint
```http
PUT /edit-profile
Content-Type: application/json

{
  "patient_id": "PAT_12345",
  "first_name": "Jane",
  "last_name": "Smith-Johnson",
  "mobile": "+1234567890",
  "address": "456 New Avenue, Cityville, State 12345",
  "emergency_contact": "+0987654321",
  "height": 166.0,
  "weight": 64.0,
  "medical_conditions": ["Diabetes"],
  "allergies": ["Peanuts"],
  "current_medications": ["Insulin"]
}
```

## Data Validation Rules

### Field Validation
- **Email**: Valid email format
- **Mobile**: 10+ digits
- **Gender**: 'Male', 'Female', 'Other'
- **Height/Weight**: Positive numbers
- **Date of Birth**: Valid date format (YYYY-MM-DD)
- **Blood Type**: Valid blood type from predefined list

### Business Rules
- **Pregnancy Week**: Must be between 1-42 weeks
- **Expected Delivery Date**: Must be calculated from LMP + 280 days
- **Age**: Must be calculated from date of birth
- **BMI**: Must be calculated from height and weight

## Error Handling

### Common Error Responses
```json
// Missing required field
{
  "error": "Missing required field: first_name"
}

// Invalid data format
{
  "error": "Invalid email format"
}

// Profile not found
{
  "error": "Patient not found"
}

// Database error
{
  "error": "Database not connected"
}
```

## Summary: Minimum Viable Complete Profile

The **absolute minimum** fields needed for a complete patient profile page are:

1. **Personal**: first_name, last_name, date_of_birth, gender, blood_type
2. **Contact**: email, mobile, emergency_contact, address  
3. **Physical**: height, weight
4. **Pregnancy**: is_pregnant, pregnancy_status, last_period_date
5. **Medical**: medical_conditions, allergies, current_medications

**Total: 15 essential fields** that ensure the patient has a complete, functional profile for the pregnancy tracking application.

## Implementation Checklist

- [ ] Create progressive form UI with 5 sections
- [ ] Implement client-side validation for all required fields
- [ ] Add auto-calculation for pregnancy week and due date
- [ ] Implement BMI calculation
- [ ] Add proper error handling and user feedback
- [ ] Create responsive design for mobile devices
- [ ] Add form progress indicator
- [ ] Implement save draft functionality
- [ ] Add field-level validation messages
- [ ] Test all API integrations
- [ ] Add accessibility features (ARIA labels, keyboard navigation)
- [ ] Implement form analytics and tracking

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [Authentication Guide](./AUTHENTICATION_GUIDE.md)
- [Pregnancy Tracking Features](./PREGNANCY_FEATURES.md)
