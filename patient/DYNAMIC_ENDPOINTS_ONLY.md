# 🔐 Dynamic Endpoints Only - Use Patient's Pregnancy Week

## ✅ **THESE ARE YOUR DYNAMIC ENDPOINTS**

All these endpoints **automatically use the logged-in patient's `pregnancy_week`** from the database.

**NO NEED TO SPECIFY WEEK NUMBER** - It's automatic! 🎉

---

## 🔐 **Authentication Required**

All endpoints require JWT token from login:

```bash
# 1. Login first
POST /login
Body: {
  "email": "patient@example.com",
  "password": "password123"
}

Response: {
  "token": "eyJhbGci...",
  "patient_id": "PAT123"
}

# 2. Use token in all requests
Headers: {
  "Authorization": "Bearer eyJhbGci..."
}
```

---

## 📋 **8 Dynamic Endpoints**

### **1️⃣ Get My Current Week**
```
GET /api/trimester/my-week
Authorization: Bearer {token}
```

**Returns**:
```json
{
  "success": true,
  "patient_id": "PAT123",
  "current_week": 15,
  "message": "Patient is at week 15"
}
```

**Purpose**: Check what pregnancy week the logged-in patient is currently in

---

### **2️⃣ Get My Week Data** ⭐ MOST USED
```
GET /api/trimester/my-data?use_openai=true&include_fruit_image=true
Authorization: Bearer {token}
```

**Returns**:
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
    "key_developments": [
      {
        "title": "Bone Strengthening",
        "description": "Bones continue to harden",
        "category": "skeletal"
      }
    ],
    "symptoms": ["Backache", "Round ligament pain"],
    "tips": ["Gentle exercise", "Stay hydrated"]
  },
  "fruit_image": "data:image/jpeg;base64,...",
  "message": "Successfully retrieved data for your current week 15"
}
```

**Purpose**: Get complete pregnancy info for YOUR current week

---

### **3️⃣ Get My Baby Image** 🖼️
```
GET /api/trimester/my-baby-image?format=stream
Authorization: Bearer {token}
```

**Returns**: Raw PNG image (e.g., Apple image if you're at week 15)

**Parameters**:
- `format`: `stream` (default, returns PNG) or `base64` (returns JSON)
- `regenerate`: `true` to force new image generation

**Purpose**: Display baby size comparison image for YOUR current week

**Example for HTML**:
```html
<img src="http://localhost:5002/api/trimester/my-baby-image?format=stream" 
     alt="My Baby Size" 
     headers='{"Authorization": "Bearer YOUR_TOKEN"}'>
```

---

### **4️⃣ Get My Enhanced Data** 🤖
```
GET /api/trimester/my-enhanced?include_rag_analysis=true&image_method=all
Authorization: Bearer {token}
```

**Returns**:
```json
{
  "success": true,
  "patient_id": "PAT123",
  "current_week": 15,
  "week": 15,
  "trimester": 2,
  "base_data": {...},
  "images": {
    "rag": {"type": "real_fruit", "data": "..."},
    "openai": {"type": "ai_generated", "data": "..."},
    "traditional": {"type": "matplotlib", "data": "..."}
  },
  "rag_analysis": {
    "personalized_developments": [...],
    "medical_advisories": [...],
    "confidence_score": 0.99
  },
  "service_status": {
    "rag_available": true,
    "openai_available": true
  }
}
```

**Purpose**: Get comprehensive analysis with RAG + AI + all image types for YOUR week

---

### **5️⃣ Get My RAG Personalized** 🎯
```
GET /api/trimester/my-rag?use_ai=true&use_mock_data=false
Authorization: Bearer {token}
```

**Returns**:
```json
{
  "patient_id": "PAT123",
  "week": 15,
  "trimester": 2,
  "personalized_developments": [
    {
      "original_development": {
        "title": "Bone Strengthening",
        "description": "Bones continue to harden"
      },
      "personalized_note": "Bones continue to harden. Given your diabetes history, blood sugar control is crucial during this development phase...",
      "medical_consideration": "Diabetes can affect fetal growth",
      "risk_level": "medium",
      "monitoring_recommendations": [
        "Daily blood glucose monitoring",
        "Nutritionist consultation",
        "Endocrinologist review"
      ]
    }
  ],
  "medical_advisories": [
    "Medication safety during pregnancy needs evaluation"
  ],
  "special_monitoring": [
    "Daily blood glucose monitoring",
    "Nutritionist consultation"
  ],
  "rag_context": "Pregnancy Week 15 Information: | Baby Size: Apple | Patient Profile: Age 28...",
  "confidence_score": 0.99
}
```

**Purpose**: Get personalized pregnancy advice based on YOUR medical history for YOUR current week

---

### **6️⃣ Get My Symptoms** 🤒
```
GET /api/trimester/my-symptoms
Authorization: Bearer {token}
```

**Returns**:
```json
{
  "success": true,
  "week": 15,
  "trimester": 2,
  "action_type": "early_symptoms",
  "data": {
    "common_symptoms": [
      "Backache",
      "Round ligament pain",
      "Increased appetite"
    ],
    "when_to_call_doctor": [
      "Severe pain",
      "Heavy bleeding",
      "Severe headache"
    ],
    "relief_tips": [
      "Gentle stretching exercises",
      "Warm compress on sore areas",
      "Maintain good posture"
    ],
    "severity_level": "mild"
  },
  "message": "Successfully generated symptoms for your current week 15"
}
```

**Purpose**: Get AI-powered symptoms information for YOUR current week

---

### **7️⃣ Get My Nutrition Tips** 🥗
```
GET /api/trimester/my-nutrition
Authorization: Bearer {token}
```

**Returns**:
```json
{
  "success": true,
  "week": 15,
  "trimester": 2,
  "action_type": "nutrition_tips",
  "data": {
    "essential_nutrients": [
      "Iron for blood production",
      "Calcium for bone development",
      "Protein for growth",
      "Vitamin D"
    ],
    "foods_to_avoid": [
      "Raw fish",
      "Unpasteurized cheese",
      "Excessive caffeine"
    ],
    "meal_suggestions": [
      "Lean proteins",
      "Dark leafy greens",
      "Whole grains"
    ],
    "hydration_tips": [
      "Drink 8-10 glasses of water daily",
      "Limit caffeine intake"
    ]
  },
  "message": "Successfully generated nutrition tips for your current week 15"
}
```

**Purpose**: Get AI nutrition recommendations for YOUR current week

---

### **8️⃣ Get My Wellness Tips** 💪
```
GET /api/trimester/my-wellness
Authorization: Bearer {token}
```

**Returns**:
```json
{
  "success": true,
  "week": 15,
  "trimester": 2,
  "action_type": "wellness_tips",
  "data": {
    "exercise_tips": [
      "Walking 30 minutes daily",
      "Prenatal yoga",
      "Swimming"
    ],
    "sleep_advice": [
      "Sleep on your left side",
      "Use pregnancy pillow",
      "Maintain sleep schedule"
    ],
    "stress_management": [
      "Meditation",
      "Deep breathing exercises",
      "Gentle prenatal massage"
    ],
    "general_wellness": [
      "Stay hydrated",
      "Take prenatal vitamins",
      "Attend prenatal appointments"
    ]
  },
  "message": "Successfully generated wellness tips for your current week 15"
}
```

**Purpose**: Get AI wellness recommendations for YOUR current week

---

## 🧪 **How to Test**

### **Step 1: Login**
Use Postman or cURL:

```bash
curl -X POST http://localhost:5002/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password"
  }'
```

Save the `token` from response.

---

### **Step 2: Test Your Current Week**
```bash
curl http://localhost:5002/api/trimester/my-week \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response**:
```json
{
  "success": true,
  "patient_id": "PAT123",
  "current_week": 15,
  "message": "Patient is at week 15"
}
```

---

### **Step 3: Get Your Baby Image**
```bash
curl http://localhost:5002/api/trimester/my-baby-image?format=stream \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  --output my_baby.png
```

**Expected**: PNG file with YOUR baby size (e.g., Apple for week 15)

---

### **Step 4: Get Personalized RAG**
```bash
curl "http://localhost:5002/api/trimester/my-rag?use_ai=true&use_mock_data=false" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected**: Personalized advice based on YOUR medical history and YOUR current week

---

## 📬 **Postman Collection**

### **Import**: `Trimester_Dynamic_Patient_Collection.json`

**What's Included**:
1. **Login Patient** - Get JWT token (auto-saves to environment)
2. **Get My Current Week** - Check your week
3. **Get My Week Data** - Full pregnancy info
4. **Get My Baby Image (Stream)** - Baby size image
5. **Get My Enhanced Data** - RAG + AI + Images
6. **Get My RAG Personalized** - Medical history-based advice
7. **Get My Symptoms** - AI symptoms
8. **Get My Nutrition Tips** - AI nutrition
9. **Get My Wellness Tips** - AI wellness

**Usage**:
1. Set `patient_email` and `patient_password` in environment
2. Run "Login Patient" - token auto-saves
3. Run any `my-*` endpoint - week is automatic!

---

## 🎯 **Key Points**

### **✅ What Makes It Dynamic:**

1. **Reads `pregnancy_week` from Patient Database**
   ```python
   patient = db.patients_collection.find_one({"patient_id": patient_id})
   current_week = patient['pregnancy_week']  # e.g., 15
   ```

2. **Extracts `patient_id` from JWT Token**
   ```python
   token → patient_id → database → pregnancy_week
   ```

3. **Uses Patient's Week Automatically**
   ```python
   # You call: /my-baby-image
   # System uses: patient's week 15
   # Returns: Apple image (week 15 baby size)
   ```

---

## 💡 **Examples**

### **Patient at Week 5**:
```bash
GET /api/trimester/my-baby-image
→ Returns: Sesame seed image
```

### **Patient at Week 15**:
```bash
GET /api/trimester/my-baby-image
→ Returns: Apple image
```

### **Patient at Week 30**:
```bash
GET /api/trimester/my-baby-image
→ Returns: Cabbage image
```

**Same endpoint, different images based on patient's week!** 🎯

---

## 🔧 **How Patient Week is Set**

The patient's `pregnancy_week` is stored in the database. It can be:

1. **Manually set** when patient registers
2. **Calculated from LMP date** (Last Menstrual Period)
3. **Updated** as pregnancy progresses

The system reads it from these fields (in order):
- `patient.pregnancy_week`
- `patient.health_data.pregnancy_week`
- `patient.health_data.pregnancy_info.current_week`
- `patient.current_pregnancy_week`

---

## ✅ **All Dynamic Endpoints Summary**

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/my-week` | Check current week | Week number |
| `/my-data` | Full week info | Developments, symptoms, tips |
| `/my-baby-image` | Baby size image | PNG/base64 for current week |
| `/my-enhanced` | Complete analysis | RAG + AI + images |
| `/my-rag` | Personalized advice | Medical history-based |
| `/my-symptoms` | Symptoms info | AI-powered for current week |
| `/my-nutrition` | Nutrition tips | AI-powered for current week |
| `/my-wellness` | Wellness tips | AI-powered for current week |

**All 8 endpoints use the patient's `pregnancy_week` from database automatically!** ✅

---

## 🎊 **READY TO USE!**

Your dynamic endpoints are ready:
- ✅ JWT authentication integrated
- ✅ Patient week auto-detected from DB
- ✅ Correct baby images per week
- ✅ RAG personalization with real medical history
- ✅ No manual week parameter needed

**Import `Trimester_Dynamic_Patient_Collection.json` and start using!** 🚀

---

## 📞 **Quick Test**

```bash
# Login
POST /login → Get token

# Check your week
GET /api/trimester/my-week → "current_week": 15

# Get your baby image
GET /api/trimester/my-baby-image?format=stream → Apple image

# Get personalized RAG
GET /api/trimester/my-rag → Medical history-based advice
```

**That's it! No week parameter needed anywhere!** 🎉


