# 📬 Trimester RAG Postman Collection - Quick Start Guide

## 🎯 **Collection Overview**

**Collection**: `Trimester_RAG_Complete_Collection.json`  
**Environment**: `Trimester_RAG_Environment.json`  
**Total Requests**: 26 endpoints organized in 6 folders  
**Server**: `http://localhost:5002`

---

## 🚀 **Quick Start**

### **Step 1: Import to Postman**

1. Open Postman
2. Click **Import** button
3. Drag and drop these files:
   - `Trimester_RAG_Complete_Collection.json`
   - `Trimester_RAG_Environment.json`
4. Click **Import**

### **Step 2: Select Environment**

1. Click the environment dropdown (top right)
2. Select **"🤖 Trimester RAG Environment"**
3. Verify `base_url` is set to `http://localhost:5002`

### **Step 3: Run Your First Request**

1. Navigate to **🏥 Health & Status** folder
2. Click **Health Check**
3. Click **Send**
4. You should see: `{"status": "healthy", "message": "Trimester API is running"}`

---

## 📁 **Collection Structure**

### **1. 🏥 Health & Status** (3 requests)
Check if services are running and configured correctly.

| Request | Purpose | Expected Response |
|---------|---------|-------------------|
| Health Check | Verify API is running | 200 OK |
| API Information | Get RAG features status | Features list with rag_enabled: true |
| OpenAI Status | Check OpenAI configuration | openai_available: true |

**Start here** to verify everything is working! ✅

---

### **2. 🤖 RAG Features (Main)** (4 requests)
Test RAG personalization with different patient profiles.

#### **RAG Personalized - Diabetes Patient**
```
GET /api/trimester/patient/15/rag?patient_id=PAT_DIABETES_123
```
**Expected**: Personalized advice with blood glucose monitoring recommendations

#### **RAG Personalized - Hypertension Patient**
```
GET /api/trimester/patient/20/rag?patient_id=PAT_HYPERTENSION_456
```
**Expected**: Blood pressure monitoring and preeclampsia screening advice

#### **RAG Personalized - Cancer History**
```
GET /api/trimester/patient/25/rag?patient_id=PAT_CANCER_789
```
**Expected**: Oncologist consultation and specialized monitoring

#### **RAG Personalized - Healthy Patient**
```
GET /api/trimester/patient/30/rag?patient_id=PAT_HEALTHY_001
```
**Expected**: Standard pregnancy monitoring recommendations

**These are the MAIN RAG features!** 🤖

---

### **3. 🔍 Semantic Search (Qdrant)** (4 requests)
Test vector similarity search using natural language.

#### **Search - Baby Development**
```
GET /api/trimester/search?query=baby+development&limit=3
```
**Expected**: Relevant weeks with baby development information, scored by similarity

#### **Search - Nutrition Tips**
```
GET /api/trimester/search?query=nutrition+tips+for+pregnancy&limit=5
```
**Expected**: Weeks with nutrition-related content

#### **Search - Second Trimester**
```
GET /api/trimester/search?query=second+trimester+symptoms&limit=5
```
**Expected**: Weeks 14-27 with symptom information

#### **Search - Exercise During Pregnancy**
```
GET /api/trimester/search?query=safe+exercise+during+pregnancy&limit=3
```
**Expected**: Weeks with exercise recommendations

**Test Qdrant vector search here!** 🔍

---

### **4. 📊 Week Data** (5 requests)
Get pregnancy week information with various options.

| Request | Features | Use Case |
|---------|----------|----------|
| Get Week 10 (Basic) | Standard data + fruit image | Basic week info |
| Get Week 20 (With OpenAI) | AI-enhanced baby size | Enhanced details |
| Get Week 15 Enhanced | RAG + AI + All images | Complete analysis |
| Get All Weeks | All 40 weeks | Full dataset |
| Get Week Developments | Only key developments | Quick summary |

---

### **5. 🍊 Trimester Data** (3 requests)
Get data organized by trimester.

#### **Get Trimester 1 Weeks**
```
GET /api/trimester/trimester/1?include_fruit_images=true
```
**Expected**: Weeks 1-13 with fruit images

#### **Get Trimester 2 Weeks**
```
GET /api/trimester/trimester/2?include_fruit_images=true
```
**Expected**: Weeks 14-27 with fruit images

#### **Trimester Fruit Recommendations (RAG)**
```
GET /api/trimester/trimester/3/fruit-recommendations?patient_id=PAT123
```
**Expected**: RAG-based fruit size recommendations for trimester 3

---

### **6. 🤖 AI Features (OpenAI)** (5 requests)
Test OpenAI-powered features.

| Request | AI Feature | Output |
|---------|------------|--------|
| AI Baby Size | GPT-3.5 baby size | Detailed size info |
| AI Symptoms | GPT-3.5 symptoms | Relief tips + warnings |
| AI Screening | GPT-3.5 screening | Test recommendations |
| AI Wellness Tips | GPT-3.5 wellness | Exercise + sleep advice |
| AI Nutrition Tips | GPT-3.5 nutrition | Meal suggestions |

---

### **7. 🖼️ Image Generation** (3 requests)
Test image generation features.

#### **Baby Image - Stream (PNG)**
```
GET /api/trimester/week/15/baby-image?format=stream
```
**Expected**: Raw PNG image file (can view directly in browser)

#### **Baby Image - Base64 (JSON)**
```
GET /api/trimester/week/15/baby-image?format=base64
```
**Expected**: JSON with base64 encoded image data

#### **Baby Image - Regenerate**
```
GET /api/trimester/week/20/baby-image?format=base64&regenerate=true
```
**Expected**: Freshly generated image from OpenAI DALL-E

---

## 🧪 **Testing Workflow**

### **Recommended Testing Order:**

1. **Start with Health Checks** ✅
   - Health Check
   - API Information
   - OpenAI Status

2. **Test RAG Personalization** 🤖
   - Diabetes Patient (see blood sugar monitoring)
   - Hypertension Patient (see BP monitoring)
   - Cancer History (see specialist recommendations)

3. **Test Semantic Search** 🔍
   - Baby Development
   - Nutrition Tips
   - Second Trimester

4. **Test Basic Week Data** 📊
   - Get Week 10
   - Get Week 20 with OpenAI
   - Get Enhanced Week 15

5. **Test AI Features** 🤖
   - AI Baby Size
   - AI Symptoms
   - AI Nutrition

6. **Test Images** 🖼️
   - Stream format
   - Base64 format

---

## ✅ **Tests Included**

### **Automated Tests (Built-in)**

Several requests include automated tests that run after each response:

#### **RAG Personalized - Diabetes Patient**
- ✅ Status code is 200
- ✅ Contains personalized developments array
- ✅ Contains medical advisories array

#### **Search - Baby Development**
- ✅ Status code is 200
- ✅ Returns search results array
- ✅ Success flag is true

**These tests run automatically!** Check the **Test Results** tab after each request.

---

## 🎯 **Expected Responses**

### **RAG Personalized Response**
```json
{
  "patient_id": "PAT_DIABETES_123",
  "week": 15,
  "trimester": 2,
  "confidence_score": 0.99,
  "personalized_developments": [
    {
      "original_development": {...},
      "personalized_note": "Given your diabetes history...",
      "medical_consideration": "Diabetes can affect fetal growth",
      "risk_level": "medium",
      "monitoring_recommendations": [
        "Daily blood glucose monitoring",
        "Nutritionist consultation"
      ]
    }
  ],
  "medical_advisories": [...],
  "special_monitoring": [...],
  "rag_context": "Pregnancy Week 15 Information..."
}
```

### **Semantic Search Response**
```json
{
  "success": true,
  "query": "baby development",
  "results": [
    {
      "week": 39,
      "trimester": 3,
      "score": 0.495,
      "content": "...",
      "key_developments": [...],
      "baby_size": {...}
    }
  ],
  "total_results": 2
}
```

---

## 🔧 **Environment Variables**

The collection uses these variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `base_url` | http://localhost:5002 | Server URL |
| `patient_id` | PAT123 | Default patient ID |
| `patient_diabetes` | PAT_DIABETES_123 | Diabetes patient |
| `patient_hypertension` | PAT_HYPERTENSION_456 | Hypertension patient |
| `patient_cancer` | PAT_CANCER_789 | Cancer history patient |
| `week` | 15 | Default week |
| `trimester` | 2 | Default trimester |
| `use_ai` | true | Enable AI features |
| `use_mock_data` | true | Use mock patient data |

You can change these in the environment settings!

---

## 🎨 **Mock Patient Profiles**

### **Diabetes Patient** (`PAT_DIABETES_123`)
- Condition: Type 2 Diabetes, moderate severity
- Treatment: Metformin, Diet management
- Recommendations: Blood glucose monitoring, nutritionist consultation

### **Hypertension Patient** (`PAT_HYPERTENSION_456`)
- Condition: Hypertension, mild severity
- Treatment: ACE inhibitor
- Recommendations: Blood pressure monitoring, preeclampsia screening

### **Cancer History** (`PAT_CANCER_789`)
- Condition: Breast Cancer, in remission
- Treatment: Chemotherapy, Radiation
- Recommendations: Oncologist consultation, specialized blood work

### **Healthy Patient** (`PAT_HEALTHY_001`)
- Condition: None
- Recommendations: Standard pregnancy monitoring

---

## 🚨 **Troubleshooting**

### **❌ Connection Refused**
**Problem**: Can't connect to server  
**Solution**: Ensure server is running at `http://localhost:5002`
```bash
cd patient
python run_app.py
```

### **❌ 503 Service Unavailable**
**Problem**: RAG services not initialized  
**Solution**: Check `.env` file has OpenAI and Qdrant credentials

### **❌ 404 Not Found**
**Problem**: Wrong endpoint URL  
**Solution**: Verify `base_url` in environment is `http://localhost:5002`

### **❌ Slow Response**
**Problem**: OpenAI/Qdrant taking time  
**Solution**: Normal for first request, subsequent requests are faster

---

## 📊 **Response Times**

| Endpoint Type | Expected Time | Notes |
|---------------|---------------|-------|
| Health Check | < 100ms | Instant |
| Basic Week Data | < 500ms | Fast |
| Semantic Search | < 1s | Qdrant query |
| RAG Personalized | 2-3s | OpenAI generation |
| AI Features | 2-4s | OpenAI API call |
| Image Generation | 3-5s | DALL-E generation |

---

## 🎉 **Success Indicators**

You'll know RAG is working when you see:

✅ **API Information** shows:
```json
{
  "features": {
    "qdrant_enabled": true,
    "semantic_search_available": true,
    "rag_personalization_available": true
  }
}
```

✅ **RAG Personalized** returns:
```json
{
  "confidence_score": 0.99,
  "personalized_developments": [...],
  "medical_advisories": [...],
  "monitoring_recommendations": [...]
}
```

✅ **Semantic Search** returns:
```json
{
  "success": true,
  "results": [...],  // with similarity scores
  "total_results": 3
}
```

---

## 📚 **Additional Resources**

- **Full Integration Guide**: `TRIMESTER_MODULE_INTEGRATION_GUIDE.md`
- **RAG Usage Guide**: `TRIMESTER_RAG_USAGE_GUIDE.md`
- **Success Summary**: `FINAL_TRIMESTER_RAG_SUCCESS.md`

---

## 🎯 **Quick Test Checklist**

Use this checklist to verify all features:

- [ ] Health Check returns 200 OK
- [ ] API Information shows RAG features enabled
- [ ] RAG Personalized works for diabetes patient
- [ ] Semantic Search returns relevant results
- [ ] Week data retrieval works
- [ ] OpenAI AI features generate responses
- [ ] Image generation returns images
- [ ] All automated tests pass

**When all items are checked, your RAG integration is verified!** ✅

---

## 🚀 **You're Ready!**

Import the collection and start testing your **RAG-powered pregnancy tracking system**!

**Happy Testing!** 🎉


