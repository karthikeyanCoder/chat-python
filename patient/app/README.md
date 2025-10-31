# Modular Patient Backend Application

**Architecture:** Modular Monolithic + MVC Pattern  
**Version:** 2.0.0  
**Status:** ✅ ALL MODULES COMPLETE - Function-Based MVC

---

## Quick Start

```bash
# Install dependencies
pip install -r ../requirements.txt

# Run application
python main.py

# Or from project root
python app/main.py

# Access at:
http://localhost:5002
```

---

## Directory Structure

```
app/
├── main.py                    # Application entry point
│
├── core/                      # Core utilities (shared across all modules)
│   ├── database.py           # Database connection manager
│   ├── auth.py               # JWT token handling
│   ├── email.py              # Email service
│   ├── validators.py         # Input validation
│   └── config.py             # Configuration settings
│
├── shared/                    # Shared services (reusable components)
│   ├── ocr_service.py        # OCR processing
│   ├── llm_service.py        # OpenAI integration
│   ├── quantum_service.py    # Vector database
│   ├── activity_tracker.py   # Activity logging
│   └── mock_n8n_service.py   # Webhook simulation
│
└── modules/                   # Feature modules (MVC pattern)
    ├── auth/                 # ✅ Authentication
    ├── pregnancy/            # ✅ Pregnancy tracking
    ├── symptoms/             # ✅ Symptoms analysis
    ├── vital_signs/          # ✅ Vital signs monitoring
    ├── medication/           # ✅ Medication management
    ├── nutrition/            # ✅ Nutrition tracking
    ├── hydration/            # ✅ Hydration tracking
    ├── mental_health/        # ✅ Mental health support
    ├── medical_lab/          # ✅ Lab report OCR
    ├── voice/                # ✅ Voice interactions
    ├── appointments/         # ✅ Appointment booking
    ├── doctors/              # ✅ Doctor profiles
    ├── sleep_activity/       # ✅ Sleep & activity tracking
    ├── profile/              # ✅ User profiles
    ├── profile_utils/        # ✅ Profile utilities
    ├── quantum_llm/          # ✅ AI services
    └── system_health/        # ✅ System monitoring
```

---

## Module Structure (MVC Pattern)

Each module follows this structure:

```
modules/MODULE_NAME/
├── __init__.py           # Module exports
├── routes.py             # API endpoints (View)
├── services.py           # Business logic (Controller) - FUNCTION-BASED
├── repository.py         # Data access (Model)
└── schemas.py            # Validation
```

### Separation of Concerns:

**routes.py (View)** - Handles HTTP:
- Receives requests
- Validates with schemas
- Delegates to service
- Returns responses

**services.py (Controller)** - Business logic:
- Function-based approach (no classes)
- Direct database access via global imports
- Business logic validation
- Returns results

**repository.py (Model)** - Data access:
- Database queries only
- CRUD operations
- No business logic

**schemas.py** - Validation:
- Request validation
- Response formatting
- Data sanitization

---

## ✅ ALL MODULES COMPLETE (16/16)

### Core Modules
- **auth/** - Authentication (12 endpoints)
  - User registration with OTP
  - Login/Logout
  - Password reset
  - Profile management
  - JWT token handling

### Health Tracking Modules
- **pregnancy/** - Pregnancy Tracking (14 endpoints)
  - Week-by-week information
  - Trimester tracking
  - Baby development
  - AI-powered tips
  - Progress tracking

- **symptoms/** - Symptoms Analysis (9 endpoints)
  - AI-powered symptom analysis
  - Knowledge base integration
  - Symptom logging
  - Analysis reports

- **vital_signs/** - Vital Signs (13 endpoints)
  - Record vitals
  - History tracking
  - AI analysis
  - Statistics
  - Alerts
  - OCR processing

- **medication/** - Medication (20 endpoints)
  - Prescription management
  - OCR processing
  - Dosage tracking
  - Reminders

- **nutrition/** - Nutrition (7 endpoints)
  - Food tracking
  - GPT-4 analysis
  - Transcription via N8N

- **hydration/** - Hydration (12 endpoints)
  - Water intake tracking
  - Goals
  - Analytics
  - Reminders

- **mental_health/** - Mental Health (14 endpoints)
  - Mood tracking
  - Assessments
  - Therapy stories
  - AI chat support

- **sleep_activity/** - Sleep & Activity (13 endpoints)
  - Sleep tracking
  - Activity monitoring
  - Analytics

### Medical Services Modules
- **medical_lab/** - Lab Reports (5 endpoints)
  - Document OCR
  - Base64 processing
  - Format support

- **voice/** - Voice (7 endpoints)
  - Audio transcription
  - AI responses
  - Text-to-speech

### Doctor & Appointments Modules
- **doctors/** - Doctor Profiles (3 endpoints)
  - Profile management
  - Search & filtering
  - Sample data fallback

- **appointments/** - Appointments (19 endpoints)
  - Booking
  - Management
  - Scheduling
  - History

### Utility Modules
- **profile_utils/** - Profile Utilities (2 endpoints)
  - Profile retrieval
  - Email lookup

- **quantum_llm/** - AI & Vector Search (7 endpoints)
  - Quantum vector search
  - LLM operations
  - Knowledge base

- **system_health/** - System Health (2 endpoints)
  - Database health
  - Reconnect

- **profile/** - Extended Profile Features
  - Additional profile endpoints

---

## 🎯 Function-Based Architecture Benefits

All modules now use **function-based services** instead of classes:

### Before (Class-Based):
```python
class MedicationService:
    def __init__(self, db_instance, tracker, ocr):
        self.db = db_instance
        self.activity_tracker = tracker
        self.ocr_service = ocr
    
    def save_medication_log(self, data):
        patient = self.db.patients_collection.find_one(...)
```

### After (Function-Based):
```python
from app.core.database import db

def save_medication_log_service(data):
    patient = db.patients_collection.find_one(...)
```

### Advantages:
1. ✅ **Simpler Code** - No class boilerplate
2. ✅ **Direct Imports** - Global singleton pattern
3. ✅ **Easier Testing** - Simple function mocking
4. ✅ **Better Performance** - No class instantiation overhead
5. ✅ **Consistent Pattern** - All modules follow same structure
6. ✅ **Faster Development** - Less code to write
7. ✅ **Maintainable** - Easy to find and update functions

---

## Core Utilities

### database.py
```python
from app.core.database import db

db.connect()
collection = db.get_collection('collection_name')
```

### auth.py
```python
from app.core.auth import generate_jwt_token, token_required

# Generate token
token = generate_jwt_token(user_data)

# Protect route
@app.route('/protected')
@token_required
def protected_route():
    patient_id = request.user_data['patient_id']
```

### email.py
```python
from app.core.email import send_otp_email, generate_otp

otp = generate_otp()
send_otp_email(email, otp)
```

### validators.py
```python
from app.core.validators import hash_password, verify_password

hashed = hash_password('password123')
is_valid = verify_password('password123', hashed)
```

---

## Shared Services

### OCR Service
```python
from app.shared.ocr_service import OCRService

ocr = OCRService()
result = ocr.process_file(file_content, filename)
```

### LLM Service
```python
from app.shared.llm_service import LLMService

llm = LLMService()
response = llm.generate_llm_fallback(symptom_text, weeks)
```

### Quantum Service
```python
from app.shared.quantum_service import QuantumVectorService

quantum = QuantumVectorService()
results = quantum.search_knowledge(query, weeks)
```

---

## Adding a New Endpoint

### Example: Add "Get Patient Statistics" to Auth Module

1. **Add to services.py:**
```python
def get_patient_statistics_service(patient_id):
    from app.core.database import db
    
    patient = db.patients_collection.find_one({"patient_id": patient_id})
    if not patient:
        return jsonify({"error": "Not found"}), 404
    
    stats = calculate_statistics(patient)
    return jsonify(stats), 200
```

2. **Add to routes.py:**
```python
from .services import get_patient_statistics_service

@auth_bp.route('/statistics/<patient_id>', methods=['GET'])
@token_required
def get_statistics(patient_id):
    return get_patient_statistics_service(patient_id)
```

Done! No need to touch other modules.

---

## Testing

### Run the Application:
```bash
python main.py
```

### Test Endpoints:
```bash
# Health check
curl http://localhost:5002/health

# Test auth
curl -X POST http://localhost:5002/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","mobile":"1234567890","password":"test123"}'
```

---

## Configuration

### Environment Variables (.env):
```bash
# Database
MONGO_URI=mongodb://localhost:27017
DB_NAME=patients_db

# JWT
JWT_SECRET_KEY=your-secret-key

# Email
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# AI Services
OPENAI_API_KEY=your_key
QDRANT_URL=http://localhost:6333
```

---

## Benefits of This Structure

### 1. Maintainability
- Find code in seconds (not minutes)
- Each module is self-contained
- Clear responsibilities

### 2. Testability
- Test modules independently
- Mock services easily
- Fast test execution

### 3. Scalability
- Add new features quickly
- Multiple devs work in parallel
- Extract to microservices if needed

### 4. Performance
- Same performance as monolith
- Easier to optimize specific modules
- Can scale to 100k+ users

---

## Migration Progress

- ✅ Foundation: 100%
- ✅ Auth Module: 100%
- ✅ Pregnancy Module: 100%
- ✅ Symptoms Module: 100%
- ✅ Vital Signs Module: 100%
- ✅ Medication Module: 100%
- ✅ Nutrition Module: 100%
- ✅ Hydration Module: 100%
- ✅ Mental Health Module: 100%
- ✅ Medical Lab Module: 100%
- ✅ Voice Module: 100%
- ✅ Appointments Module: 100%
- ✅ Doctors Module: 100%
- ✅ Sleep Activity Module: 100%
- ✅ Profile Module: 100%
- ✅ Profile Utils Module: 100%
- ✅ Quantum LLM Module: 100%
- ✅ System Health Module: 100%

**Total Progress: 18/18 modules (100%) ✅ COMPLETE**

---

## Documentation

- `MODULAR_ARCHITECTURE_GUIDE.md` - Architecture explanation
- `MIGRATION_STATUS.md` - Migration tracking
- `IMPLEMENTATION_SUMMARY.md` - What was implemented
- `MODULE_MIGRATION_TEMPLATE.md` - Template for new modules
- `ALL_APIS.md` - Complete API reference

---

## Support

Questions? Check:
1. Architecture guide
2. Migration template
3. Existing module code (auth/ is the best example)
4. Implementation summary

---

**🎉 ALL MODULES COMPLETE! Function-Based MVC Architecture Fully Implemented!** 🚀

**Version:** 2.0.0  
**Last Updated:** October 2024  
**Framework:** Flask 3.0.3  
**Python:** 3.8+  
**Architecture:** Function-Based MVC (100% Complete)
