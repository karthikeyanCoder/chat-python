# 🚀 Quick Start Guide - Patient Appointments with Availability

## 📥 Import Instructions

### 1. Import Collection
1. Open Postman
2. Click **Import** button
3. Select `Patient_Appointments_with_Availability.postman_collection.json`
4. Click **Import**

### 2. Import Environment
1. Click **Import** button
2. Select `Patient_Appointments_Environment.json`
3. Click **Import**
4. Select the imported environment from dropdown

## 🎯 5-Minute Test Run

### Step 1: Login (30 seconds)
1. Open **🔐 Authentication** folder
2. Run **"1. Patient Login"**
3. ✅ Check: Token saved to environment

### Step 2: Find Doctor (30 seconds)
1. Open **👨‍⚕️ Doctor Discovery** folder
2. Run **"1. Get All Doctors"**
3. ✅ Check: Doctor list received

### Step 3: Check Availability (1 minute)
1. Open **📅 Doctor Availability** folder
2. Run **"1. Get Doctor Availability"**
3. ✅ Check: Available slots shown

### Step 4: Book Appointment (2 minutes)
1. Open **📋 Appointment Management** folder
2. Run **"2. Create Appointment (with Slot)"**
3. ✅ Check: Appointment created successfully

### Step 5: Verify Booking (30 seconds)
1. Run **"1. Get Patient Appointments"**
2. ✅ Check: Your appointment appears in list

## 🔧 Environment Setup

### Required Variables
| Variable | Value | Auto-Set |
|----------|-------|----------|
| `base_url` | `http://localhost:5002` | ❌ |
| `auth_token` | JWT token | ✅ |
| `patient_id` | Patient ID | ✅ |
| `doctor_id` | `D17597286260221902` | ❌ |
| `appointment_date` | Tomorrow's date | ✅ |
| `appointment_type` | `consultation` | ❌ |
| `slot_id` | Available slot | ✅ |
| `appointment_id` | Created appointment | ✅ |

### Optional Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `patient_email` | `patient@example.com` | Test patient email |
| `patient_password` | `password123` | Test patient password |
| `specialization` | `Obstetrics and Gynecology` | Doctor specialization |

## 🎨 Customization

### Change Doctor
1. Update `doctor_id` in environment
2. Use a different doctor ID from the doctors list

### Change Date
1. Update `appointment_date` in environment
2. Format: `YYYY-MM-DD` (e.g., `2024-01-30`)

### Change Appointment Type
1. Update `appointment_type` in environment
2. Options: `consultation`, `follow-up`, `first-visit`, `report-review`

### Change Base URL
1. Update `base_url` in environment
2. For production: `https://your-api-domain.com`
3. For different port: `http://localhost:5003`

## 🔄 Common Workflows

### Complete Booking Flow
```
Login → Get Doctors → Check Availability → Book Appointment → Verify
```

### Video Call Booking
```
Login → Get Doctors → Check Availability → Book Video Call → Verify
```

### Appointment Management
```
Login → Get Appointments → Update Appointment → Cancel Appointment
```

### Availability Checking
```
Login → Get Doctor Profile → Check Availability → Get Specific Slots
```

## ⚠️ Troubleshooting

### Login Fails
- ✅ Check patient credentials
- ✅ Verify patient app is running
- ✅ Check base_url is correct

### No Available Slots
- ✅ Try different date
- ✅ Try different doctor
- ✅ Check appointment_type

### Appointment Creation Fails
- ✅ Verify slot_id is valid
- ✅ Check appointment_date format
- ✅ Ensure all required fields present

### Token Expired
- ✅ Re-run "1. Patient Login"
- ✅ Token automatically refreshed

## 📊 Test Data

### Sample Patient Credentials
```json
{
  "login_identifier": "patient@example.com",
  "password": "password123"
}
```

### Sample Doctor ID
```
D17597286260221902
```

### Sample Appointment Data
```json
{
  "appointment_date": "2024-01-30",
  "appointment_time": "10:00",
  "type": "consultation",
  "appointment_type": "in-person",
  "notes": "Regular checkup appointment"
}
```

## 🎯 Success Indicators

### Login Success
- Status: `200 OK`
- Response contains `token` and `patient_id`
- Environment variables updated

### Availability Success
- Status: `200 OK`
- Response contains `slots` array
- `slot_id` saved to environment

### Booking Success
- Status: `201 Created`
- Response contains `appointment_id`
- Appointment appears in appointments list

## 🚀 Advanced Usage

### Batch Testing
1. Use Postman Runner
2. Select collection
3. Set iterations
4. Run automated tests

### API Monitoring
1. Set up Postman Monitor
2. Schedule regular runs
3. Monitor API health

### Team Collaboration
1. Share collection via Postman workspace
2. Export/import environment
3. Use version control

## 📞 Support

### Quick Help
- Check Postman console for logs
- Verify environment variables
- Review response status codes

### Common Issues
- **401 Unauthorized**: Re-login
- **404 Not Found**: Check doctor_id
- **400 Bad Request**: Check request body
- **500 Server Error**: Check server logs

---

**Ready to test! 🎉**
