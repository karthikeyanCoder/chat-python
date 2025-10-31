# 📖 Doctor Invite & Connection APIs - Quick Reference

## 🚀 Base URL
```
http://localhost:5000
```

---

## 🔐 Authentication

All endpoints except "Verify Invite" require doctor JWT token:

```bash
Authorization: Bearer YOUR_DOCTOR_TOKEN
```

Get token from login:
```bash
POST /doctor-login
Body: {"login_identifier": "doctor@example.com", "password": "pass123"}
```

---

## 📌 Quick API List

| # | Method | Endpoint | Auth | Description |
|---|--------|----------|------|-------------|
| 1 | POST | `/api/doctor/generate-invite` | ✅ | Generate invite code |
| 2 | GET | `/api/invite/verify/<code>` | ❌ | Verify code (public) |
| 3 | GET | `/api/doctor/invites` | ✅ | List my invites |
| 4 | GET | `/api/doctor/connection-requests` | ✅ | View requests |
| 5 | POST | `/api/doctor/respond-to-request` | ✅ | Accept/reject |
| 6 | POST | `/api/doctor/remove-connection` | ✅ | Remove connection |
| 7 | GET | `/api/doctor/connected-patients` | ✅ | List connected |

---

## 📝 API Details

### **1. Generate Invite**
```bash
POST /api/doctor/generate-invite
Headers: Authorization: Bearer <token>
Body: {
  "patient_email": "patient@example.com",
  "expires_in_days": 7,
  "message": "Welcome message"
}
Response: {
  "invite_code": "ABC-XYZ-123",
  "expires_at": "2025-10-28T10:00:00Z"
}
```

### **2. Verify Invite (Public)**
```bash
GET /api/invite/verify/ABC-XYZ-123
(No auth required)
Response: {
  "valid": true,
  "doctor": { "name": "Dr. John", "specialty": "OB/GYN" }
}
```

### **3. List My Invites**
```bash
GET /api/doctor/invites?status=active
Headers: Authorization: Bearer <token>
Response: {
  "invites": [
    {
      "invite_code": "ABC-XYZ-123",
      "patient_email": "patient@example.com",
      "status": "active"
    }
  ]
}
```

### **4. View Connection Requests**
```bash
GET /api/doctor/connection-requests?status=pending
Headers: Authorization: Bearer <token>
Response: {
  "requests": [
    {
      "connection_id": "CONN123",
      "patient_name": "Jane Doe",
      "status": "pending"
    }
  ]
}
```

### **5. Accept/Reject Request**
```bash
POST /api/doctor/respond-to-request
Headers: Authorization: Bearer <token>
Body: {
  "connection_id": "CONN123",
  "action": "accept",  # or "reject"
  "message": "Welcome!"
}
Response: {
  "message": "Patient connection accepted",
  "status": "active"
}
```

### **6. Remove Connection**
```bash
POST /api/doctor/remove-connection
Headers: Authorization: Bearer <token>
Body: {
  "connection_id": "CONN123",
  "reason": "Patient relocated"
}
Response: {
  "message": "Connection removed successfully"
}
```

### **7. List Connected Patients**
```bash
GET /api/doctor/connected-patients
Headers: Authorization: Bearer <token>
Response: {
  "patients": [
    {
      "patient_id": "PAT123",
      "name": "Jane Doe",
      "pregnancy_info": { "is_pregnant": true, "week": 12 }
    }
  ],
  "summary": { "total_count": 1 }
}
```

---

## 🔄 Common Workflows

### **Doctor Invites Patient**
```
1. POST /api/doctor/generate-invite → Get code
2. Share code with patient
3. Patient uses code
4. Connection created (active)
```

### **Patient Requests Doctor**
```
1. Patient sends request
2. GET /api/doctor/connection-requests → See request
3. POST /api/doctor/respond-to-request → Accept
4. Connection active
```

---

## 🧪 Testing with cURL

### **Complete Test Sequence**

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/doctor-login \
  -H "Content-Type: application/json" \
  -d '{"login_identifier":"doctor@example.com","password":"pass123"}' \
  | jq -r '.token')

# 2. Generate Invite
CODE=$(curl -s -X POST http://localhost:5000/api/doctor/generate-invite \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_email":"patient@example.com","expires_in_days":7}' \
  | jq -r '.invite.invite_code')

echo "Invite Code: $CODE"

# 3. Verify Invite (No auth)
curl http://localhost:5000/api/invite/verify/$CODE

# 4. Get My Invites
curl http://localhost:5000/api/doctor/invites \
  -H "Authorization: Bearer $TOKEN"

# 5. Get Connection Requests
curl "http://localhost:5000/api/doctor/connection-requests?status=pending" \
  -H "Authorization: Bearer $TOKEN"

# 6. Accept Request (replace CONN_ID)
curl -X POST http://localhost:5000/api/doctor/respond-to-request \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"connection_id":"CONN123","action":"accept","message":"Welcome!"}'

# 7. Get Connected Patients
curl http://localhost:5000/api/doctor/connected-patients \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎨 Flutter Code Snippets

### **Generate Invite**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/doctor/generate-invite'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'patient_email': email,
    'expires_in_days': 7,
    'message': message,
  }),
);
```

### **Accept Request**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/doctor/respond-to-request'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'connection_id': connectionId,
    'action': 'accept',
    'message': welcomeMessage,
  }),
);
```

---

## 📊 Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process data |
| 201 | Created | Invite generated |
| 400 | Bad Request | Check input |
| 401 | Unauthorized | Check token |
| 403 | Forbidden | Not your resource |
| 404 | Not Found | Invalid ID/code |
| 500 | Server Error | Contact support |

---

## 🚨 Common Errors

### **"Doctor authentication required"**
```json
{"success": false, "error": "Doctor authentication required"}
```
**Fix:** Ensure token contains `doctor_id` field

### **"Connection already exists"**
```json
{"success": false, "error": "Connection already exists with this patient"}
```
**Fix:** Patient already connected to this doctor

### **"Invalid invite code format"**
```json
{"success": false, "error": "Invalid invite code format"}
```
**Fix:** Code must be XXX-XXX-XXX format

### **"Invite code has expired"**
```json
{"success": false, "error": "Invite code has expired"}
```
**Fix:** Generate new invite code

---

## 🔍 Query Parameters

### **Get Invites**
```
?status=active   # Active invites only
?status=expired  # Expired invites only
?status=used     # Used invites only
(no param)       # All invites
```

### **Get Connection Requests**
```
?status=pending   # Pending only (default)
?status=active    # Active connections
?status=rejected  # Rejected requests
?status=all       # All requests
```

---

## 🎯 Pro Tips

### **Invite Code Format**
Always: `ABC-XYZ-123` (3 groups of 3 alphanumeric, uppercase)

### **Token in Header**
```
Authorization: Bearer <token>
```
NOT:
```
Authorization: <token>  ❌
Bearer <token>          ❌
```

### **JSON Content-Type**
Always include for POST requests:
```
Content-Type: application/json
```

### **Status Filters**
Use query parameters for filtering:
```
/api/doctor/invites?status=active
/api/doctor/connection-requests?status=pending
```

---

## 📦 Postman Collection

**File:** `Doctor_Invite_Connection_Postman_Collection.json`

**Import Steps:**
1. Open Postman
2. Import → File → Select JSON
3. Collection appears with 7 requests
4. Run "Doctor Login" first
5. Token auto-saves
6. Test other endpoints

---

## 🔗 Related Documentation

| File | Purpose |
|------|---------|
| `MERGE_SUMMARY.md` | Complete merge overview |
| `INVITE_CONNECTION_MERGE_COMPLETE.md` | Detailed merge process |
| `DOCTOR_INVITE_API_GUIDE.md` | Comprehensive API guide |
| `API_QUICK_REFERENCE.md` | This file - Quick reference |

---

## ⚡ TL;DR - Copy-Paste Ready

```bash
# 1. Login
curl -X POST http://localhost:5000/doctor-login \
  -H "Content-Type: application/json" \
  -d '{"login_identifier":"doctor@example.com","password":"pass"}'

# 2. Generate Invite (replace TOKEN)
curl -X POST http://localhost:5000/api/doctor/generate-invite \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_email":"patient@example.com","expires_in_days":7}'

# 3. Verify Invite (replace CODE)
curl http://localhost:5000/api/invite/verify/ABC-XYZ-123

# 4. View Requests (replace TOKEN)
curl "http://localhost:5000/api/doctor/connection-requests?status=pending" \
  -H "Authorization: Bearer TOKEN"

# 5. Accept Request (replace TOKEN and CONN_ID)
curl -X POST http://localhost:5000/api/doctor/respond-to-request \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"connection_id":"CONN_ID","action":"accept","message":"Welcome!"}'

# 6. Get Connected Patients (replace TOKEN)
curl http://localhost:5000/api/doctor/connected-patients \
  -H "Authorization: Bearer TOKEN"
```

---

**Keep this file handy for quick reference!** 📌

**Version:** 1.0  
**Updated:** October 21, 2025












