# Patient AI Summary Postman Collection

This Postman collection provides comprehensive testing for the Patient AI Summary API endpoints, including OpenAI integration for generating medical summaries.

## 📋 Collection Overview

The collection includes the following main sections:

1. **Authentication** - Doctor login to get access token
2. **Patient AI Summary** - AI-powered medical summary generation
3. **Related Endpoints** - Supporting endpoints for health data
4. **Health Check** - API server health verification

## 🚀 Quick Start

### Prerequisites
- Postman installed
- Backend server running on `http://localhost:5000`
- OpenAI API key configured
- Test doctor account credentials

### OpenAI API Key Setup
**IMPORTANT:** Before using AI summary endpoints, configure your OpenAI API key:

1. **Get OpenAI API Key:**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key (starts with `sk-`)

2. **Configure Environment Variable:**
   ```bash
   # Add to your .env file
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

3. **Restart Backend Server:**
   ```bash
   python app_mvc.py
   ```

### Import the Collection
1. Open Postman
2. Click "Import" button
3. Select `Patient_AI_Summary_Postman_Collection.json`
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

## 📊 AI Summary Endpoints

### 1. Get Patient AI Summary
**Endpoint:** `GET /doctor/patient/{patient_id}/ai-summary`

**Purpose:** Generate AI-powered medical summary using OpenAI GPT-3.5-turbo

**Headers:**
```
Authorization: Bearer {auth_token}
```

**Example Request:**
```
GET http://localhost:5000/doctor/patient/PAT1758712159E182A3/ai-summary
```

**Example Response:**
```json
{
  "success": true,
  "patient_id": "PAT1758712159E182A3",
  "patient_name": "John Doe",
  "ai_summary": "COMPREHENSIVE MEDICAL SUMMARY\n\nPATIENT OVERVIEW:\nJohn Doe is a 28-year-old male patient with a comprehensive health profile...\n\nHEALTH DATA ANALYSIS:\n- The patient has logged 3 food entries, indicating good nutrition tracking habits\n- 1 symptom analysis report suggests proactive health monitoring\n- 1 mental health log entry shows attention to mental well-being\n- 1 medication entry indicates current medication management\n- 1 appointment scheduled demonstrates regular medical care\n\nKEY CONCERNS & RECOMMENDATIONS:\n1. Continue regular health monitoring through the platform\n2. Maintain consistent medication adherence\n3. Consider expanding mental health logging for better trend analysis\n4. Regular follow-up appointments are recommended\n\nOVERALL HEALTH ASSESSMENT:\nThe patient demonstrates good health awareness and proactive monitoring.\n\nPRIORITY AREAS FOR MEDICAL ATTENTION:\n- Monitor medication compliance and effectiveness\n- Review symptom patterns for any emerging health concerns\n- Assess mental health trends for overall well-being\n- Ensure regular medical check-ups continue",
  "summary_stats": {
    "total_medications": 1,
    "total_symptoms": 1,
    "total_food_entries": 3,
    "total_tablet_logs": 0,
    "total_kick_logs": 0,
    "total_mental_health": 1,
    "total_prescriptions": 0,
    "total_vital_signs": 0,
    "total_appointments": 1
  }
}
```

### 2. Get Patient Full Details (Prerequisite)
**Endpoint:** `GET /doctor/patient/{patient_id}/full-details`

**Purpose:** Retrieve comprehensive patient data that serves as input for AI summary

**Headers:**
```
Authorization: Bearer {auth_token}
```

**Description:** This endpoint is automatically called by the AI summary endpoint to gather all patient data for analysis.

## 🤖 AI Analysis Process

### Data Sources Analyzed
The AI summary endpoint automatically collects and analyzes:

1. **Patient Information**
   - Demographics (name, age, gender, blood type)
   - Contact information and emergency contacts
   - Pregnancy status (if applicable)

2. **Health Data Categories**
   - **Appointments** - Medical appointments and consultations
   - **Food & Nutrition** - Dietary logs and nutritional tracking
   - **Symptoms** - Symptom analysis reports and health concerns
   - **Mental Health** - Mental health logs and assessments
   - **Medications** - Medication history and compliance
   - **Kick Counts** - Fetal movement tracking (for pregnant patients)
   - **Prescriptions** - Prescription documents and medications
   - **Vital Signs** - Blood pressure, heart rate, temperature, etc.
   - **Tablet Logs** - Medication adherence tracking

3. **Summary Statistics**
   - Total counts for each health data category
   - Recent activity patterns
   - Data completeness indicators

### AI Processing Details
- **Model:** OpenAI GPT-3.5-turbo
- **Max Tokens:** 1000
- **Temperature:** 0.3 (for consistent, professional output)
- **System Role:** Medical AI assistant
- **Analysis Focus:**
  1. Patient Overview
  2. Health Data Analysis
  3. Key Concerns & Recommendations
  4. Overall Health Assessment
  5. Priority Areas for Medical Attention

## 📝 Response Fields Explained

### Main Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Indicates if the request was successful |
| `patient_id` | String | The patient identifier used in the request |
| `patient_name` | String | Full name of the patient |
| `ai_summary` | String | AI-generated medical summary text |
| `summary_stats` | Object | Statistical summary of patient data |

### Summary Stats Object

| Field | Type | Description |
|-------|------|-------------|
| `total_appointments` | Integer | Number of medical appointments |
| `total_food_entries` | Integer | Number of nutrition logs |
| `total_symptoms` | Integer | Number of symptom reports |
| `total_mental_health` | Integer | Number of mental health logs |
| `total_medications` | Integer | Number of medication entries |
| `total_kick_logs` | Integer | Number of fetal movement logs |
| `total_prescriptions` | Integer | Number of prescription documents |
| `total_vital_signs` | Integer | Number of vital signs entries |
| `total_tablet_logs` | Integer | Number of medication adherence logs |

## 🚨 Error Responses

### Common Error Codes

#### 500 Internal Server Error - OpenAI API Key Missing
```json
{
  "success": false,
  "message": "Failed to generate AI summary"
}
```
**Cause:** OpenAI API key not configured in environment variables

#### 404 Not Found - Patient Not Found
```json
{
  "success": false,
  "message": "Patient not found"
}
```

#### 401 Unauthorized - Missing Authentication
```json
{
  "error": "Unauthorized access"
}
```

#### 400 Bad Request - Invalid Patient Data
```json
{
  "success": false,
  "message": "Failed to get patient data"
}
```

## 🔧 Collection Variables

The collection uses the following variables:

- `base_url`: API server base URL (default: http://localhost:5000)
- `doctor_id`: Doctor ID (auto-populated after login)
- `patient_id`: Patient ID for testing (default: PAT1758712159E182A3)
- `auth_token`: Authentication token (auto-populated after login)

## 🧪 Testing Scenarios

### Success Scenarios
1. **Valid Login** - Login with correct credentials
2. **Get AI Summary** - Generate AI summary for existing patient
3. **Get Full Details** - Retrieve comprehensive patient data
4. **Related Endpoints** - Test supporting health data endpoints

### Error Scenarios
1. **Missing OpenAI Key** - Test without OpenAI API key configured
2. **Invalid Patient ID** - Test with non-existent patient
3. **Missing Token** - Access endpoints without authentication
4. **OpenAI API Errors** - Test with invalid OpenAI API key

## 🔄 Workflow Example

1. **Setup OpenAI API Key**
   ```bash
   echo "OPENAI_API_KEY=sk-your-key-here" >> .env
   python app_mvc.py
   ```

2. **Run Health Check**
   - Execute "API Health Check" request
   - Verify server is running

3. **Authenticate**
   - Run "Doctor Login" request
   - Verify token is saved

4. **Test Patient Data**
   - Run "Get Patient Full Details" request
   - Verify patient data is available

5. **Generate AI Summary**
   - Run "Get Patient AI Summary" request
   - Verify AI summary is generated

6. **Review Results**
   - Check AI summary content
   - Verify summary stats are accurate

## 💡 Best Practices

### For Developers
1. **Cache AI Summaries** - Avoid regenerating summaries for unchanged data
2. **Error Handling** - Always check the `success` field before using `ai_summary`
3. **Rate Limiting** - Implement client-side rate limiting for AI requests
4. **Cost Monitoring** - Monitor OpenAI API usage and costs

### For Medical Professionals
1. **Review AI Output** - Always review AI-generated summaries before making decisions
2. **Data Freshness** - Ensure patient data is up-to-date before generating summaries
3. **Comprehensive Analysis** - Use AI summaries as a starting point, not final diagnosis
4. **Documentation** - Keep records of AI-generated insights

## 🐛 Troubleshooting

### Common Issues

#### 1. "OpenAI API key not found"
**Solution:** Add `OPENAI_API_KEY=your_key_here` to your `.env` file and restart the server.

#### 2. "Failed to generate AI summary"
**Possible Causes:**
- OpenAI API key invalid or expired
- OpenAI API quota exceeded
- Network connectivity issues
- Invalid patient data

#### 3. "Patient not found"
**Solution:** Verify the patient ID exists in the database.

#### 4. "Unauthorized access"
**Solution:** Ensure you're sending a valid Bearer token in the Authorization header.

### Debug Steps

1. **Check Server Logs:**
   ```bash
   # Look for OpenAI API errors
   tail -f server.log | grep -i openai
   ```

2. **Verify API Key:**
   ```bash
   # Test OpenAI API key directly
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

3. **Test Patient Data:**
   ```bash
   # Verify patient exists and has data
   curl -X GET "http://localhost:5000/doctor/patient/PATIENT_ID/full-details" \
        -H "Authorization: Bearer YOUR_TOKEN"
   ```

## 📚 Additional Resources

- **Backend API Documentation**: Check `controllers/doctor_controller.py` for implementation details
- **OpenAI Documentation**: [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- **Patient Data Structure**: Check `models/patient_model.py` for data structure details

## 📞 Support

For technical issues:
1. Check server logs for detailed error messages
2. Verify OpenAI API key configuration
3. Test with different patient IDs
4. Ensure network connectivity to OpenAI API

For medical concerns:
- AI summaries are for informational purposes only
- Always consult with qualified medical professionals
- Do not rely solely on AI-generated medical advice

---

**Note:** This endpoint requires OpenAI API access and may incur costs based on usage. Monitor your OpenAI API usage and costs regularly.
