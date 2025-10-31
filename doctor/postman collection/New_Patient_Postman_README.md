# New Patient CRUD API - Postman Collection

## 📋 **Overview**

This Postman collection provides comprehensive testing for the New Patient CRUD (Create, Read, Update, Delete) API endpoints. The collection includes all necessary requests with sample data and expected responses.

## 🚀 **Quick Start**

### **1. Import Collection**
1. Open Postman
2. Click "Import" button
3. Select `New_Patient_Postman_Collection.json`
4. The collection will be imported with all requests and examples

### **2. Set Environment Variables**
- **baseUrl**: `http://localhost:8000` (already set in collection)
- **patientId**: Will be auto-populated after creating a patient

### **3. Start Backend Server**
```bash
python app_mvc.py
```
The server will run on `http://localhost:8000`

## 📚 **API Endpoints**

### **1. Health Check**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/health`
- **Purpose**: Verify server is running
- **Expected Response**: 200 OK with health status

### **2. Create New Patient**
- **Method**: `POST`
- **URL**: `{{baseUrl}}/patients`
- **Purpose**: Create a new patient record
- **Required Fields**: `full_name`, `date_of_birth`, `contact_number`, `email`

#### **Sample Request Body:**
```json
{
  "full_name": "John Doe",
  "date_of_birth": "15/03/1985",
  "contact_number": "9876543210",
  "email": "john.doe@example.com",
  "gender": "Male",
  "address": "123 Main Street, Downtown",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_number": "9876543211",
  "medical_notes": "No known medical conditions",
  "allergies": "None",
  "blood_type": "O+",
  "is_active": true
}
```

#### **Success Response (201 Created):**
```json
{
  "message": "Patient created successfully",
  "patient_id": "PAT1758892220123456",
  "status": "success"
}
```

#### **Error Responses:**
- **400 Bad Request**: Missing required fields or validation errors
- **409 Conflict**: Email already exists
- **500 Internal Server Error**: Server-side errors

### **3. Get Patient by ID**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Retrieve a specific patient's details
- **Expected Response**: 200 OK with patient data or 404 Not Found

### **4. Get All Patients**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients?page=1&limit=10`
- **Purpose**: Retrieve all patients with pagination
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `limit`: Number of patients per page (default: 20)
  - `search`: Search term for filtering

### **5. Search Patients**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients?search=John`
- **Purpose**: Search patients by name, email, or patient ID
- **Query Parameters**:
  - `search`: Search term

### **6. Update Patient**
- **Method**: `PUT`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Update patient information
- **Body**: JSON with fields to update

#### **Sample Update Request:**
```json
{
  "city": "Los Angeles",
  "state": "CA",
  "pincode": "90210",
  "medical_notes": "Updated: Patient has mild asthma"
}
```

### **7. Delete Patient**
- **Method**: `DELETE`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Delete a patient record
- **Expected Response**: 200 OK with success message or 404 Not Found

### **8. Get Patients by Doctor**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/doctors/{doctor_id}/patients`
- **Purpose**: Get all patients assigned to a specific doctor

## 🧪 **Testing Workflow**

### **Step 1: Health Check**
1. Run "Health Check" request
2. Verify server is running (200 OK response)

### **Step 2: Create Patient**
1. Run "Create New Patient" request
2. Copy the `patient_id` from response
3. Set the `patientId` variable in Postman

### **Step 3: Verify Creation**
1. Run "Get Patient by ID" request
2. Verify patient data is correct

### **Step 4: Test Search**
1. Run "Search Patients" request
2. Verify search functionality works

### **Step 5: Update Patient**
1. Run "Update Patient" request
2. Verify changes are applied

### **Step 6: Test List**
1. Run "Get All Patients" request
2. Verify patient appears in list

### **Step 7: Clean Up**
1. Run "Delete Patient" request
2. Verify patient is deleted

## 📊 **Expected Data Structure**

### **Patient Object:**
```json
{
  "_id": "MongoDB ObjectId",
  "patient_id": "PAT{timestamp}{hash}",
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
  "assigned_doctor_id": "",
  "is_active": true,
  "created_at": "2025-09-26T18:41:36.247325Z",
  "updated_at": "2025-09-26T18:41:36.247325Z"
}
```

## ⚠️ **Validation Rules**

### **Required Fields:**
- `full_name`: Must not be empty
- `date_of_birth`: Must be in DD/MM/YYYY format
- `contact_number`: Must be at least 10 digits
- `email`: Must be valid email format

### **Email Validation:**
- Must contain '@' symbol
- Must have valid domain with '.'
- Must be unique (no duplicates)

### **Contact Number Validation:**
- Must be at least 10 digits
- Can contain numbers, spaces, dashes, parentheses

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Connection Refused (Error 10061)**
   - Ensure backend server is running
   - Check if port 8000 is available
   - Verify `baseUrl` is correct

2. **Database Collection Not Available (Error 500)**
   - Check MongoDB connection
   - Verify database is accessible
   - Check server logs for details

3. **Validation Errors (Error 400)**
   - Check required fields are provided
   - Verify email format is correct
   - Ensure contact number is valid

4. **Patient Not Found (Error 404)**
   - Verify patient ID is correct
   - Check if patient exists in database
   - Ensure patient hasn't been deleted

### **Debug Steps:**
1. Check server logs for detailed error messages
2. Verify database connection status
3. Test with minimal required fields first
4. Check network connectivity

## 📱 **Flutter Integration**

The Flutter app uses these same endpoints:
- **Create Patient**: `POST /patients`
- **Get Patient**: `GET /patients/{id}`
- **Update Patient**: `PUT /patients/{id}`
- **Delete Patient**: `DELETE /patients/{id}`
- **Search Patients**: `GET /patients?search={term}`

## 🎯 **Success Criteria**

✅ **All tests pass**  
✅ **Patient creation works**  
✅ **Patient retrieval works**  
✅ **Patient update works**  
✅ **Patient deletion works**  
✅ **Search functionality works**  
✅ **Validation errors handled properly**  
✅ **Error responses are clear and helpful**  

---

**🎉 Ready to test! Import the collection and start testing the New Patient CRUD API!**

## 📋 **Overview**

This Postman collection provides comprehensive testing for the New Patient CRUD (Create, Read, Update, Delete) API endpoints. The collection includes all necessary requests with sample data and expected responses.

## 🚀 **Quick Start**

### **1. Import Collection**
1. Open Postman
2. Click "Import" button
3. Select `New_Patient_Postman_Collection.json`
4. The collection will be imported with all requests and examples

### **2. Set Environment Variables**
- **baseUrl**: `http://localhost:8000` (already set in collection)
- **patientId**: Will be auto-populated after creating a patient

### **3. Start Backend Server**
```bash
python app_mvc.py
```
The server will run on `http://localhost:8000`

## 📚 **API Endpoints**

### **1. Health Check**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/health`
- **Purpose**: Verify server is running
- **Expected Response**: 200 OK with health status

### **2. Create New Patient**
- **Method**: `POST`
- **URL**: `{{baseUrl}}/patients`
- **Purpose**: Create a new patient record
- **Required Fields**: `full_name`, `date_of_birth`, `contact_number`, `email`

#### **Sample Request Body:**
```json
{
  "full_name": "John Doe",
  "date_of_birth": "15/03/1985",
  "contact_number": "9876543210",
  "email": "john.doe@example.com",
  "gender": "Male",
  "address": "123 Main Street, Downtown",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_number": "9876543211",
  "medical_notes": "No known medical conditions",
  "allergies": "None",
  "blood_type": "O+",
  "is_active": true
}
```

#### **Success Response (201 Created):**
```json
{
  "message": "Patient created successfully",
  "patient_id": "PAT1758892220123456",
  "status": "success"
}
```

#### **Error Responses:**
- **400 Bad Request**: Missing required fields or validation errors
- **409 Conflict**: Email already exists
- **500 Internal Server Error**: Server-side errors

### **3. Get Patient by ID**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Retrieve a specific patient's details
- **Expected Response**: 200 OK with patient data or 404 Not Found

### **4. Get All Patients**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients?page=1&limit=10`
- **Purpose**: Retrieve all patients with pagination
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `limit`: Number of patients per page (default: 20)
  - `search`: Search term for filtering

### **5. Search Patients**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients?search=John`
- **Purpose**: Search patients by name, email, or patient ID
- **Query Parameters**:
  - `search`: Search term

### **6. Update Patient**
- **Method**: `PUT`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Update patient information
- **Body**: JSON with fields to update

#### **Sample Update Request:**
```json
{
  "city": "Los Angeles",
  "state": "CA",
  "pincode": "90210",
  "medical_notes": "Updated: Patient has mild asthma"
}
```

### **7. Delete Patient**
- **Method**: `DELETE`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Delete a patient record
- **Expected Response**: 200 OK with success message or 404 Not Found

### **8. Get Patients by Doctor**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/doctors/{doctor_id}/patients`
- **Purpose**: Get all patients assigned to a specific doctor

## 🧪 **Testing Workflow**

### **Step 1: Health Check**
1. Run "Health Check" request
2. Verify server is running (200 OK response)

### **Step 2: Create Patient**
1. Run "Create New Patient" request
2. Copy the `patient_id` from response
3. Set the `patientId` variable in Postman

### **Step 3: Verify Creation**
1. Run "Get Patient by ID" request
2. Verify patient data is correct

### **Step 4: Test Search**
1. Run "Search Patients" request
2. Verify search functionality works

### **Step 5: Update Patient**
1. Run "Update Patient" request
2. Verify changes are applied

### **Step 6: Test List**
1. Run "Get All Patients" request
2. Verify patient appears in list

### **Step 7: Clean Up**
1. Run "Delete Patient" request
2. Verify patient is deleted

## 📊 **Expected Data Structure**

### **Patient Object:**
```json
{
  "_id": "MongoDB ObjectId",
  "patient_id": "PAT{timestamp}{hash}",
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
  "assigned_doctor_id": "",
  "is_active": true,
  "created_at": "2025-09-26T18:41:36.247325Z",
  "updated_at": "2025-09-26T18:41:36.247325Z"
}
```

## ⚠️ **Validation Rules**

### **Required Fields:**
- `full_name`: Must not be empty
- `date_of_birth`: Must be in DD/MM/YYYY format
- `contact_number`: Must be at least 10 digits
- `email`: Must be valid email format

### **Email Validation:**
- Must contain '@' symbol
- Must have valid domain with '.'
- Must be unique (no duplicates)

### **Contact Number Validation:**
- Must be at least 10 digits
- Can contain numbers, spaces, dashes, parentheses

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Connection Refused (Error 10061)**
   - Ensure backend server is running
   - Check if port 8000 is available
   - Verify `baseUrl` is correct

2. **Database Collection Not Available (Error 500)**
   - Check MongoDB connection
   - Verify database is accessible
   - Check server logs for details

3. **Validation Errors (Error 400)**
   - Check required fields are provided
   - Verify email format is correct
   - Ensure contact number is valid

4. **Patient Not Found (Error 404)**
   - Verify patient ID is correct
   - Check if patient exists in database
   - Ensure patient hasn't been deleted

### **Debug Steps:**
1. Check server logs for detailed error messages
2. Verify database connection status
3. Test with minimal required fields first
4. Check network connectivity

## 📱 **Flutter Integration**

The Flutter app uses these same endpoints:
- **Create Patient**: `POST /patients`
- **Get Patient**: `GET /patients/{id}`
- **Update Patient**: `PUT /patients/{id}`
- **Delete Patient**: `DELETE /patients/{id}`
- **Search Patients**: `GET /patients?search={term}`

## 🎯 **Success Criteria**

✅ **All tests pass**  
✅ **Patient creation works**  
✅ **Patient retrieval works**  
✅ **Patient update works**  
✅ **Patient deletion works**  
✅ **Search functionality works**  
✅ **Validation errors handled properly**  
✅ **Error responses are clear and helpful**  

---

**🎉 Ready to test! Import the collection and start testing the New Patient CRUD API!**

## 📋 **Overview**

This Postman collection provides comprehensive testing for the New Patient CRUD (Create, Read, Update, Delete) API endpoints. The collection includes all necessary requests with sample data and expected responses.

## 🚀 **Quick Start**

### **1. Import Collection**
1. Open Postman
2. Click "Import" button
3. Select `New_Patient_Postman_Collection.json`
4. The collection will be imported with all requests and examples

### **2. Set Environment Variables**
- **baseUrl**: `http://localhost:8000` (already set in collection)
- **patientId**: Will be auto-populated after creating a patient

### **3. Start Backend Server**
```bash
python app_mvc.py
```
The server will run on `http://localhost:8000`

## 📚 **API Endpoints**

### **1. Health Check**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/health`
- **Purpose**: Verify server is running
- **Expected Response**: 200 OK with health status

### **2. Create New Patient**
- **Method**: `POST`
- **URL**: `{{baseUrl}}/patients`
- **Purpose**: Create a new patient record
- **Required Fields**: `full_name`, `date_of_birth`, `contact_number`, `email`

#### **Sample Request Body:**
```json
{
  "full_name": "John Doe",
  "date_of_birth": "15/03/1985",
  "contact_number": "9876543210",
  "email": "john.doe@example.com",
  "gender": "Male",
  "address": "123 Main Street, Downtown",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_number": "9876543211",
  "medical_notes": "No known medical conditions",
  "allergies": "None",
  "blood_type": "O+",
  "is_active": true
}
```

#### **Success Response (201 Created):**
```json
{
  "message": "Patient created successfully",
  "patient_id": "PAT1758892220123456",
  "status": "success"
}
```

#### **Error Responses:**
- **400 Bad Request**: Missing required fields or validation errors
- **409 Conflict**: Email already exists
- **500 Internal Server Error**: Server-side errors

### **3. Get Patient by ID**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Retrieve a specific patient's details
- **Expected Response**: 200 OK with patient data or 404 Not Found

### **4. Get All Patients**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients?page=1&limit=10`
- **Purpose**: Retrieve all patients with pagination
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `limit`: Number of patients per page (default: 20)
  - `search`: Search term for filtering

### **5. Search Patients**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/patients?search=John`
- **Purpose**: Search patients by name, email, or patient ID
- **Query Parameters**:
  - `search`: Search term

### **6. Update Patient**
- **Method**: `PUT`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Update patient information
- **Body**: JSON with fields to update

#### **Sample Update Request:**
```json
{
  "city": "Los Angeles",
  "state": "CA",
  "pincode": "90210",
  "medical_notes": "Updated: Patient has mild asthma"
}
```

### **7. Delete Patient**
- **Method**: `DELETE`
- **URL**: `{{baseUrl}}/patients/{{patientId}}`
- **Purpose**: Delete a patient record
- **Expected Response**: 200 OK with success message or 404 Not Found

### **8. Get Patients by Doctor**
- **Method**: `GET`
- **URL**: `{{baseUrl}}/doctors/{doctor_id}/patients`
- **Purpose**: Get all patients assigned to a specific doctor

## 🧪 **Testing Workflow**

### **Step 1: Health Check**
1. Run "Health Check" request
2. Verify server is running (200 OK response)

### **Step 2: Create Patient**
1. Run "Create New Patient" request
2. Copy the `patient_id` from response
3. Set the `patientId` variable in Postman

### **Step 3: Verify Creation**
1. Run "Get Patient by ID" request
2. Verify patient data is correct

### **Step 4: Test Search**
1. Run "Search Patients" request
2. Verify search functionality works

### **Step 5: Update Patient**
1. Run "Update Patient" request
2. Verify changes are applied

### **Step 6: Test List**
1. Run "Get All Patients" request
2. Verify patient appears in list

### **Step 7: Clean Up**
1. Run "Delete Patient" request
2. Verify patient is deleted

## 📊 **Expected Data Structure**

### **Patient Object:**
```json
{
  "_id": "MongoDB ObjectId",
  "patient_id": "PAT{timestamp}{hash}",
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
  "assigned_doctor_id": "",
  "is_active": true,
  "created_at": "2025-09-26T18:41:36.247325Z",
  "updated_at": "2025-09-26T18:41:36.247325Z"
}
```

## ⚠️ **Validation Rules**

### **Required Fields:**
- `full_name`: Must not be empty
- `date_of_birth`: Must be in DD/MM/YYYY format
- `contact_number`: Must be at least 10 digits
- `email`: Must be valid email format

### **Email Validation:**
- Must contain '@' symbol
- Must have valid domain with '.'
- Must be unique (no duplicates)

### **Contact Number Validation:**
- Must be at least 10 digits
- Can contain numbers, spaces, dashes, parentheses

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Connection Refused (Error 10061)**
   - Ensure backend server is running
   - Check if port 8000 is available
   - Verify `baseUrl` is correct

2. **Database Collection Not Available (Error 500)**
   - Check MongoDB connection
   - Verify database is accessible
   - Check server logs for details

3. **Validation Errors (Error 400)**
   - Check required fields are provided
   - Verify email format is correct
   - Ensure contact number is valid

4. **Patient Not Found (Error 404)**
   - Verify patient ID is correct
   - Check if patient exists in database
   - Ensure patient hasn't been deleted

### **Debug Steps:**
1. Check server logs for detailed error messages
2. Verify database connection status
3. Test with minimal required fields first
4. Check network connectivity

## 📱 **Flutter Integration**

The Flutter app uses these same endpoints:
- **Create Patient**: `POST /patients`
- **Get Patient**: `GET /patients/{id}`
- **Update Patient**: `PUT /patients/{id}`
- **Delete Patient**: `DELETE /patients/{id}`
- **Search Patients**: `GET /patients?search={term}`

## 🎯 **Success Criteria**

✅ **All tests pass**  
✅ **Patient creation works**  
✅ **Patient retrieval works**  
✅ **Patient update works**  
✅ **Patient deletion works**  
✅ **Search functionality works**  
✅ **Validation errors handled properly**  
✅ **Error responses are clear and helpful**  

---

**🎉 Ready to test! Import the collection and start testing the New Patient CRUD API!**
