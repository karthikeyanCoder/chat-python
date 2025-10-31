# Testing the Appointment Reminder System

## Quick Setup

### 1. Install Dependencies
```bash
cd doctor
pip install APScheduler==3.10.4
```

### 2. Start the Server
```bash
python app_mvc.py
```

You should see:
```
✅ Appointment reminder scheduler initialized
⏰ Reminders configured: 24 hours before appointments
🔄 Scheduler checks every 60 minutes
```

## Testing Endpoints

### 1. Test Reminder Email (POST /scheduler/test-reminder)
**Purpose**: Test email sending functionality

**Request:**
```bash
POST http://localhost:5000/scheduler/test-reminder
Content-Type: application/json

{
  "patient_email": "ramyayashva@gmail.com",
  "patient_name": "Test Patient",
  "doctor_name": "Dr. Sarah Johnson",
  "appointment_date": "2025-10-28",
  "appointment_time": "10:00:00",
  "appointment_type": "Consultation"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Email sent successfully via smtp.gmail.com:465"
}
```

### 2. Check Scheduler Status (GET /scheduler/status)
**Purpose**: Verify scheduler is running

**Request:**
```bash
GET http://localhost:5000/scheduler/status
```

**Expected Response:**
```json
{
  "success": true,
  "status": "running",
  "is_running": true,
  "message": "Scheduler is operational"
}
```

### 3. Manually Trigger Check (POST /scheduler/trigger-check)
**Purpose**: Immediately check for appointments needing reminders

**Request:**
```bash
POST http://localhost:5000/scheduler/trigger-check
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Appointment check triggered successfully"
}
```

### 4. Get Configuration (GET /scheduler/config)
**Purpose**: View current scheduler settings

**Request:**
```bash
GET http://localhost:5000/scheduler/config
```

**Expected Response:**
```json
{
  "success": true,
  "config": {
    "reminder_hours_before": 24,
    "check_interval_minutes": 60
  }
}
```

### 5. View Email Example (GET /scheduler/email-example)
**Purpose**: See what the reminder email looks like

**Request:**
```bash
GET http://localhost:5000/scheduler/email-example
```

## Testing with Postman

1. Import the collection: `Appointment_Reminder_Scheduler.postman_collection.json`
2. Run the requests in order:
   - Get Scheduler Status
   - Test Send Reminder Email
   - Trigger Appointment Check Now
   - Get Scheduler Configuration

## End-to-End Testing

### Test Complete Flow

1. **Create a Test Appointment** (24 hours in future):
```bash
POST http://localhost:5000/doctor/appointments
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "PAT176154757083BA75",
  "appointment_date": "2025-10-28",
  "appointment_time": "10:00:00",
  "appointment_type": "consultation"
}
```

2. **Verify Appointment Created**:
```bash
GET http://localhost:5000/doctor/appointments/{{appointment_id}}
```

3. **Manually Trigger Check**:
```bash
POST http://localhost:5000/scheduler/trigger-check
```

4. **Check Email**: Verify patient received the reminder email

5. **Verify Reminder Flag**: Check that `reminder_sent: true` in appointment

## Troubleshooting

### "Scheduler service is not initialized"
- Ensure APScheduler is installed: `pip install APScheduler==3.10.4`
- Check server logs for scheduler initialization errors
- Restart the server

### "Email configuration not found"
- Verify `.env` file has `SENDER_EMAIL` and `SENDER_PASSWORD`
- Check email service is working: test with `/scheduler/test-reminder`

### "No upcoming appointments found"
- Create an appointment that is 24 hours in the future
- Ensure appointment status is "scheduled" or "confirmed"
- Verify `reminder_sent` is `false`

## Configuration Options

Edit these environment variables in `.env`:

```env
REMINDER_HOURS_BEFORE=24        # Hours before appointment to send reminder
SCHEDULER_CHECK_INTERVAL=60     # Minutes between scheduler checks
```

## Expected Behavior

- **Automatic**: Scheduler runs every 60 minutes
- **Window**: Sends reminders for appointments in next 24 hours
- **Once Only**: Each appointment gets reminder sent only once
- **Status Filter**: Only sends for "scheduled" or "confirmed" appointments

