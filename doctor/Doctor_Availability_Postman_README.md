# Doctor Availability System - Postman Collection

## 📋 Overview

This Postman collection provides comprehensive testing for the Doctor Availability System using the user's proposed model structure. The system allows doctors to create availability slots and patients to view available appointments.

## 🚀 Quick Start

### 1. Import Collection
- Open Postman
- Click "Import" button
- Select `Doctor_Availability_Postman_Collection.json`
- The collection will be imported with all endpoints and variables

### 2. Set Environment Variables
The collection includes these variables:
- `base_url`: `http://localhost:5000` (default)
- `doctor_id`: `DOC123` (test doctor ID)
- `test_date`: `2025-10-26` (test date)
- `jwt_token`: Mock JWT token for testing
- `availability_id`: `AVAIL_123456789` (for update/delete operations)

### 3. Start the Server
```bash
cd doctor
python start_availability_system.py
```

## 📁 Collection Structure

### 🔐 Authentication
- **Doctor Login**: Login to get JWT token

### 👨‍⚕️ Doctor Availability Management (Protected Routes)
1. **Create Daily Availability** - POST `/doctor/{doctor_id}/availability`
2. **Get All Doctor Availability** - GET `/doctor/{doctor_id}/availability`
3. **Get Availability by Date** - GET `/doctor/{doctor_id}/availability/{date}`
4. **Get Available Slots by Type** - GET `/doctor/{doctor_id}/availability/{date}/{type}`
5. **Update Availability** - PUT `/availability/{availability_id}`
6. **Delete Availability** - DELETE `/availability/{availability_id}`

### 🌐 Public Availability (Patient View)
1. **Public - Get Doctor Availability** - GET `/public/doctor/{doctor_id}/availability/{date}`
2. **Public - Get Available Slots by Type** - GET `/public/doctor/{doctor_id}/availability/{date}/{type}`
3. **Public - Get Follow-up Slots** - GET `/public/doctor/{doctor_id}/availability/{date}/Follow-up`
4. **Public - Get First Visit Slots** - GET `/public/doctor/{doctor_id}/availability/{date}/First Visit`
5. **Public - Get Report Review Slots** - GET `/public/doctor/{doctor_id}/availability/{date}/Report Review`

### 🧪 Test Scenarios
1. **Test Invalid Date Format** - Should return 400 error
2. **Test Missing Required Fields** - Should return 400 error
3. **Test Invalid Time Format** - Should return 400 error
4. **Test Unauthorized Access** - Should return 401 error
5. **Test Invalid Doctor ID** - Should return 401 error

### 📊 Sample Responses
- **Successful Creation Response** - 201 Created
- **Availability Data Response** - 200 OK with full data structure

## 🎯 Testing Sequence

### Step 1: Authentication
1. Run "Doctor Login" to get a real JWT token
2. Update the `jwt_token` variable with the received token

### Step 2: Create Availability
1. Run "1. Create Daily Availability"
2. Copy the `availability_id` from response
3. Update the `availability_id` variable

### Step 3: Test Retrieval
1. Run "2. Get All Doctor Availability"
2. Run "3. Get Availability by Date"
3. Run "4. Get Available Slots by Type"

### Step 4: Test Public Endpoints
1. Run "Public - Get Doctor Availability" (no auth required)
2. Run "Public - Get Available Slots by Type"

### Step 5: Test Updates
1. Run "5. Update Availability"
2. Run "6. Delete Availability"

### Step 6: Test Error Scenarios
1. Run all "Test Scenarios" to verify error handling

## 📝 Request/Response Examples

### Create Availability Request
```json
{
  "date": "2025-10-26",
  "work_hours": {
    "start_time": "09:00",
    "end_time": "17:00"
  },
  "consultation_type": "Online",
  "types": [
    {
      "type": "Consultation",
      "duration_mins": 30,
      "price": 150.0,
      "currency": "USD",
      "slots": [
        { "start_time": "09:00", "end_time": "09:30", "is_booked": false },
        { "start_time": "09:30", "end_time": "10:00", "is_booked": false }
      ]
    }
  ]
}
```

### Success Response
```json
{
  "success": true,
  "message": "Availability created successfully",
  "availability_id": "AVAIL_17325648001234567890"
}
```

### Availability Data Response
```json
{
  "success": true,
  "availability": [
    {
      "availability_id": "AVAIL_17325648001234567890",
      "doctor_id": "DOC123",
      "date": "2025-10-26",
      "work_hours": {
        "start_time": "09:00",
        "end_time": "17:00"
      },
      "consultation_type": "Online",
      "types": [
        {
          "type": "Consultation",
          "duration_mins": 30,
          "price": 150.0,
          "currency": "USD",
          "available_slots_count": 2,
          "total_slots_count": 3,
          "slots": [...]
        }
      ],
      "breaks": [...],
      "is_active": true,
      "created_at": "2025-10-24T10:00:00Z",
      "updated_at": "2025-10-24T10:00:00Z"
    }
  ],
  "total_count": 1
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Connection Error**
   - Ensure server is running on `http://localhost:5000`
   - Check if `python start_availability_system.py` is running

2. **401 Unauthorized**
   - Verify JWT token is valid and not expired
   - Check if Authorization header is properly set
   - Ensure doctor_id in URL matches token

3. **400 Bad Request**
   - Verify JSON format matches the model structure
   - Check required fields are present
   - Validate date format (YYYY-MM-DD)
   - Validate time format (HH:MM)

4. **500 Internal Server Error**
   - Check server logs for database connection issues
   - Verify environment variables are set
   - Check MongoDB connection

### Environment Variables Required
```bash
MONGO_URI=mongodb://your-mongodb-connection-string
DB_NAME=your-database-name
JWT_SECRET_KEY=your-jwt-secret-key
```

## 📊 Expected Status Codes

- **200 OK**: Successful GET requests
- **201 Created**: Successful POST requests
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server/database error

## 🎯 Model Structure

The system uses the user's proposed model structure with:
- **Multi-type appointments**: Consultation, Follow-up, First Visit, Report Review
- **Flexible durations**: Each type has different duration
- **Pricing**: Each appointment type has its own price
- **Slot management**: Individual slots with booking status
- **Break periods**: Lunch breaks and blocked times

## 📈 Performance Testing

For load testing, you can:
1. Duplicate the collection
2. Use Postman's Collection Runner
3. Set iterations and delays
4. Monitor response times and error rates

## 🔄 Integration with Patient System

The public endpoints are designed to integrate with the patient system:
- Patients can view doctor availability without authentication
- Patients can filter by appointment type
- Patients can see pricing and available slots
- Integration points for booking system

## 📞 Support

If you encounter issues:
1. Check server logs
2. Verify database connection
3. Test with the provided test scripts
4. Review the model implementation

---

**Happy Testing! 🚀**
