# 🔐 Dynamic Week Endpoints Guide

## ✅ **NEW FEATURE: Automatic Week Detection!**

The trimester module now includes **7 new endpoints** that automatically use the **logged-in patient's pregnancy week** from the database!

---

## 🎯 **How It Works**

### **Traditional Endpoints** (Manual Week)
```bash
GET /api/trimester/week/20/baby-image
# You specify week 20 manually
```

### **NEW Dynamic Endpoints** (Auto Week)
```bash
GET /api/trimester/my-baby-image
# Automatically uses YOUR current pregnancy week from database
```

**No need to specify the week - it's automatic!** 🎉

---

## 🔐 **Authentication Required**

All dynamic `my-*` endpoints require JWT authentication:

### **1. Login First**
```bash
POST /login
{
  "email": "patient@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "patient_id": "PAT123"
}
```

### **2. Use Token in Requests**
```bash
GET /api/trimester/my-week
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📋 **7 New Dynamic Endpoints**

### **1. Get My Current Week** 🔍
```bash
GET /api/trimester/my-week
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "patient_id": "PAT123",
  "current_week": 15,
  "message": "Patient is at week 15"
}
```

**Use Case**: Check what week the patient is currently in

---

### **2. Get My Week Data** 📊
```bash
GET /api/trimester/my-data?use_openai=true&include_fruit_image=true
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "patient_id": "PAT123",
  "current_week": 15,
  "data": {
    "week": 15,
    "trimester": 2,
    "baby_size": {
      "size": "Apple",
      "weight": "70g",
      "length": "10.1cm"
    },
    "key_developments": [...],
    "symptoms": [...],
    "tips": [...]
  },
  "fruit_image": "data:image/jpeg;base64,...",
  "fruit_image_available": true
}
```

**Use Case**: Get complete pregnancy information for patient's current week

---

### **3. Get My Baby Image** 🖼️
```bash
GET /api/trimester/my-baby-image?format=stream
Headers: Authorization: Bearer {token}
```

**Response**: Raw PNG image of baby size (e.g., Apple for week 15)

**Use Case**: Display baby size image based on patient's current week

---

### **4. Get My Enhanced Data** 🤖
```bash
GET /api/trimester/my-enhanced?include_rag_analysis=true&image_method=all
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "patient_id": "PAT123",
  "current_week": 15,
  "week": 15,
  "trimester": 2,
  "base_data": {...},
  "images": {
    "rag": {...},
    "openai": {...},
    "traditional": {...}
  },
  "rag_analysis": {
    "personalized_developments": [...],
    "medical_advisories": [...],
    "confidence_score": 0.99
  }
}
```

**Use Case**: Get comprehensive analysis with all image types and RAG personalization

---

### **5. Get My RAG Personalized** 🎯
```bash
GET /api/trimester/my-rag?use_ai=true&use_mock_data=false
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "patient_id": "PAT123",
  "week": 15,
  "trimester": 2,
  "personalized_developments": [
    {
      "original_development": {...},
      "personalized_note": "Given your diabetes history...",
      "medical_consideration": "Blood sugar control crucial",
      "risk_level": "medium",
      "monitoring_recommendations": [
        "Daily blood glucose monitoring",
        "Nutritionist consultation"
      ]
    }
  ],
  "medical_advisories": [...],
  "special_monitoring": [...],
  "confidence_score": 0.99
}
```

**Use Case**: Get personalized advice based on YOUR medical history for YOUR current week

---

### **6. Get My Symptoms** 🤒
```bash
GET /api/trimester/my-symptoms
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "week": 15,
  "trimester": 2,
  "action_type": "early_symptoms",
  "data": {
    "common_symptoms": ["Backache", "Round ligament pain"],
    "when_to_call_doctor": ["Severe pain", "Heavy bleeding"],
    "relief_tips": ["Gentle stretching", "Warm compress"],
    "severity_level": "mild"
  }
}
```

**Use Case**: Get symptoms info for YOUR current week

---

### **7. Get My Nutrition Tips** 🥗
```bash
GET /api/trimester/my-nutrition
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "week": 15,
  "trimester": 2,
  "action_type": "nutrition_tips",
  "data": {
    "essential_nutrients": ["Iron", "Calcium", "Protein"],
    "foods_to_avoid": ["Raw fish", "Unpasteurized cheese"],
    "meal_suggestions": [...],
    "hydration_tips": [...]
  }
}
```

**Use Case**: Get nutrition advice for YOUR current week

---

### **8. Get My Wellness Tips** 💪
```bash
GET /api/trimester/my-wellness
Headers: Authorization: Bearer {token}
```

**Response**:
```json
{
  "success": true,
  "week": 15,
  "trimester": 2,
  "action_type": "wellness_tips",
  "data": {
    "exercise_tips": ["Walking", "Prenatal yoga"],
    "sleep_advice": ["Sleep on side", "Use pregnancy pillow"],
    "stress_management": ["Meditation", "Deep breathing"],
    "general_wellness": [...]
  }
}
```

**Use Case**: Get wellness tips for YOUR current week

---

## 🧪 **Testing Workflow**

### **Step 1: Login**
```bash
POST /login
{
  "email": "patient@example.com",
  "password": "password123"
}

# Save the token from response
```

### **Step 2: Check Your Week**
```bash
GET /api/trimester/my-week
Authorization: Bearer {your_token}

Response:
{
  "current_week": 15,
  "patient_id": "PAT123"
}
```

### **Step 3: Get Your Data**
```bash
GET /api/trimester/my-data
Authorization: Bearer {your_token}

# Automatically uses week 15 (your current week)
```

### **Step 4: Get Your Baby Image**
```bash
GET /api/trimester/my-baby-image?format=stream
Authorization: Bearer {your_token}

# Automatically generates image for Apple (week 15 baby size)
```

---

## 📊 **Comparison**

| Feature | Static Endpoints | Dynamic Endpoints |
|---------|------------------|-------------------|
| **Week Parameter** | Manual (`/week/20`) | Automatic (from DB) |
| **Authentication** | Optional | Required (JWT) |
| **Patient ID** | Manual query param | From JWT token |
| **Use Case** | Browse any week | Get MY current info |
| **URL Pattern** | `/week/{week}/*` | `/my-*` |

---

## 🎯 **When to Use Each**

### **Use Static Endpoints** (`/week/{week}/*`)
- Browsing different weeks
- Educational content
- No login required
- Testing with mock data

### **Use Dynamic Endpoints** (`/my-*`)
- Patient dashboard
- Personalized tracking
- Current week information
- Real patient data
- Medical history integration

---

## 🔧 **How Patient Week is Determined**

The system checks in this order:
1. `patient.pregnancy_week`
2. `patient.health_data.pregnancy_week`
3. `patient.health_data.pregnancy_info.current_week`
4. `patient.current_pregnancy_week`
5. **Default: Week 1** (if nothing found)

---

## 📬 **Postman Collection**

### **Collection**: `Trimester_Dynamic_Patient_Collection.json`

**Features**:
- ✅ Auto-saves JWT token after login
- ✅ Automatically adds Authorization header
- ✅ 8 dynamic endpoints ready to test
- ✅ Pre-configured environment variables

### **Quick Start**:
1. Import `Trimester_Dynamic_Patient_Collection.json`
2. Set `patient_email` and `patient_password` in environment
3. Run "Login Patient" request
4. JWT token is auto-saved
5. Run any `my-*` endpoint - no need to specify week!

---

## ✅ **Success Indicators**

Dynamic endpoints are working when:

✅ Login returns JWT token  
✅ `/my-week` returns your current pregnancy week  
✅ `/my-data` returns data for YOUR week (not week 1)  
✅ `/my-baby-image` generates image for YOUR baby size  
✅ `/my-rag` includes YOUR medical history  

---

## 🎉 **Benefits**

### **For Patients:**
- ✅ No need to remember current week
- ✅ Automatically personalized
- ✅ Shows relevant baby size image
- ✅ Considers medical history

### **For Developers:**
- ✅ Simpler API calls
- ✅ Automatic patient context
- ✅ Secure with JWT
- ✅ Real patient data integration

---

## 🚀 **You're Ready!**

Now you have **2 ways to use the trimester module**:

1. **Static**: Browse any week with `/week/{week}/*` endpoints
2. **Dynamic**: Get YOUR current week with `/my-*` endpoints

**Import the `Trimester_Dynamic_Patient_Collection.json` and test with your logged-in patient!** 🎊


