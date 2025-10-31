# Appointment Reminder Scheduler API Endpoints

## Overview

The appointment reminder system includes several API endpoints to manage, test, and monitor the scheduler functionality.

## Endpoints

### 1. GET /scheduler/status
Check if the scheduler is running

**Response:**
```json
{
  "success": true,
  "status": "running",
  "is_running": true,
  "message": "Scheduler is operational"
}
```

### 2. POST /scheduler/test-reminder
Test sending a reminder email (doesn't create appointment, just tests email)

**Request Body:**
```json
{
  "patient_email": "ramyayashva@gmail.com",
  "patient_name": "Test Patient",
  "doctor_name": "Dr. Sarah Johnson",
  "appointment_date": "2025-10-28",
  "appointment_time": "10:00:00",
  "appointment_type": "Consultation"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully via smtp.gmail.com:465"
}
```

### 3. POST /scheduler/trigger-check
Manually trigger the scheduler to check for upcoming appointments and send reminders immediately

**Response:**
```json
{
  "success": true,
  "message": "Appointment check triggered successfully"
}
```

### 4. GET /scheduler/config
Get current scheduler configuration

**Response:**
```json
{
  "success": true,
  "config": {
    "reminder_hours_before": 24,
    "check_interval_minutes": 60
  }
}
```

### 5. PUT /scheduler/config
Update scheduler configuration

**Request Body:**
```json
{
  "reminder_hours_before": 12,
  "check_interval_minutes": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "config": {
    "reminder_hours_before": 12,
    "check_interval_minutes": 30
  }
}
```

### 6. GET /scheduler/email-example
Get an example of the reminder email

**Response:**
```json
{
  "success": true,
  "example": {
    "to": "patient@example.com",
    "subject": "Appointment Reminder - Monday, October 28, 2024 at 10:00 AM",
    "body": "Hello Test Patient,\n\nThis is a reminder for your upcoming appointment:\n\nDate: Monday, October 28, 2024\nTime: 10:00 AM\nType: Test Appointment\nDoctor: Dr. Test Doctor\n\nPlease arrive 10 minutes early for check-in.\n\nIf you need to reschedule, please contact us.\n\nBest regards,\nPatient Alert System Team"
  }
}
```

## Using the Postman Collection

1. Import the collection: `doctor/postman collection/Appointment_Reminder_Scheduler.postman_collection.json`
2. Set the base URL variable if needed (default: http://localhost:5000)
3. Test each endpoint

## Quick Test Flow

1. **Check Status**: `GET /scheduler/status`
2. **Test Email**: `POST /scheduler/test-reminder` (with test data)
3. **Manual Trigger**: `POST /scheduler/trigger-check` (if you want to check now)
4. **View Config**: `GET /scheduler/config`
5. **View Email Example**: `GET /scheduler/email-example`

## Important Notes

- The scheduler runs automatically every 60 minutes by default
- Reminders are sent 24 hours before appointments by default
- The scheduler only sends reminders once per appointment (`reminder_sent` flag)
- The test endpoint doesn't create actual appointments, just tests email sending

