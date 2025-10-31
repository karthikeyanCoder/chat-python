# Patient Alert System API - Flask Framework

## 🏥 Healthcare Management System (Flask Version)

A comprehensive healthcare management system built with **Flask**, following a **Modular Monolithic Architecture** with **MVC Pattern**.

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Modules](#-api-modules)
- [Authentication](#-authentication)
- [Database](#-database)
- [Testing](#-testing)
- [Deployment](#-deployment)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Redis (optional, for caching)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mobile-patient-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=patient_alert_system

# JWT Secret
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# OpenAI API (optional)
OPENAI_API_KEY=your-openai-api-key

# Qdrant Vector Database (optional)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-api-key
```

### Run the Application

```bash
# Using the provided run script
python run_app.py

# The server will start at:
# http://localhost:5001
```

---

## 🏗️ Architecture

### Modular Monolithic Architecture

```
mobile-patient-backend/
│
├── app/
│   ├── core/                    # Core functionality
│   │   ├── database.py          # MongoDB connection
│   │   ├── auth.py              # JWT authentication
│   │   ├── email.py             # Email service
│   │   └── config.py            # Configuration
│   │
│   ├── shared/                  # Shared services
│   │   ├── activity_tracker.py # User activity tracking
│   │   ├── ocr_service.py       # OCR processing
│   │   ├── quantum_service.py   # Vector database
│   │   ├── llm_service.py       # LLM integration
│   │   └── mock_n8n_service.py  # Workflow automation
│   │
│   └── modules/                 # Feature modules (MVC)
│       ├── auth/
│       │   ├── routes.py        # Flask routes
│       │   ├── services.py      # Business logic
│       │   ├── repository.py    # Data access
│       │   └── schemas.py       # Data validation
│       │
│       ├── pregnancy/           # Pregnancy tracking
│       ├── symptoms/            # Symptom checker
│       ├── vital_signs/         # Vital signs monitoring
│       ├── medication/          # Medication management
│       ├── nutrition/           # Nutrition tracking
│       ├── hydration/           # Hydration tracking
│       ├── mental_health/       # Mental health support
│       ├── medical_lab/         # Lab report processing
│       ├── voice/               # Voice interactions
│       ├── appointments/        # Appointment management
│       ├── doctors/             # Doctor profiles
│       ├── sleep_activity/      # Sleep & activity tracking
│       ├── profile/             # User profiles
│       ├── profile_utils/       # Profile utilities
│       ├── quantum_llm/         # AI services
│       └── system_health/       # System monitoring
│
├── run_app.py                   # Flask entry point
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables
```

---

## ✨ Features

### 🔐 Authentication & Authorization
- User registration with OTP verification
- JWT-based authentication
- Password reset functionality
- Profile management

### 🤰 Pregnancy Tracking
- Week-by-week pregnancy information
- Baby size comparisons
- Trimester-specific advice
- AI-powered insights

### 🩺 Health Monitoring
- Symptom checker with AI analysis
- Vital signs tracking (BP, heart rate, temperature, SpO2)
- Medical lab report OCR processing
- Sleep and activity tracking

### 💊 Medication Management
- Prescription upload and OCR
- Medication reminders
- Dosage tracking
- Drug interaction warnings

### 🍎 Nutrition & Hydration
- Food intake tracking
- Calorie counting
- Water intake monitoring
- Nutritional advice

### 🧠 Mental Health
- Mood tracking
- Mental health assessments
- AI-powered therapy stories
- Chat support

### 👨‍⚕️ Doctor Services
- Doctor profiles
- Appointment scheduling
- Consultation management
- Prescription management

### 🎙️ Voice Features
- Voice transcription
- Voice-to-text conversion
- AI voice responses

---

## 📦 Installation Details

### Required Dependencies

```txt
Flask==3.0.3
Flask-CORS==4.0.1
pymongo==4.6.1
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib==1.7.4
email-validator==2.1.0
Pillow==10.2.0
openai==1.12.0
qdrant-client==1.7.3
sentence-transformers==2.3.1
```

### Optional Dependencies

```txt
# OCR Processing
pymupdf>=1.23.0
paddlepaddle==2.5.2
paddleocr==2.7.0.3

# Audio Processing
SpeechRecognition==3.10.0
pydub==0.25.1
```

---

## ⚙️ Configuration

### MongoDB Setup

#### Local MongoDB
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data

# MongoDB will run on: mongodb://localhost:27017/
```

#### MongoDB Atlas (Cloud)
1. Create account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create cluster
3. Get connection string
4. Update `.env`:
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
```

### Email Configuration (Gmail)

1. Enable 2-Factor Authentication
2. Generate App Password
3. Update `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
```

---

## 🏃 Running the Application

### Development Mode

```bash
# Start Flask server with auto-reload
python run_app.py

# Server runs on http://localhost:5001
```

### Production Mode

```bash
# Using Gunicorn (recommended)
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5001 "app.main:create_app()"

# -w 4: 4 worker processes
# -b 0.0.0.0:5001: Bind to all interfaces on port 5001
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app.main:create_app()"]
```

```bash
# Build and run
docker build -t patient-alert-api .
docker run -p 5001:5001 --env-file .env patient-alert-api
```

---

## 📚 API Modules

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/send-otp` | Send OTP to email |
| POST | `/verify-otp` | Verify OTP |
| POST | `/login` | User login |
| POST | `/logout` | User logout |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password |
| GET | `/profile` | Get user profile |
| PUT | `/edit-profile` | Update profile |

### Pregnancy (`/pregnancy`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/save-pregnancy-info` | Save pregnancy data |
| GET | `/get-pregnancy-info/<patient_id>` | Get pregnancy info |
| POST | `/generate-baby-size-image` | Generate baby image |
| GET | `/get-trimester-info/<week>` | Get trimester details |

### Symptoms (`/symptoms`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/check` | Check symptoms |
| POST | `/save` | Save symptom report |
| GET | `/history/<patient_id>` | Get symptom history |

### Vital Signs (`/vital-signs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/log` | Log vital signs |
| GET | `/history/<patient_id>` | Get vital history |
| GET | `/latest/<patient_id>` | Get latest vitals |
| POST | `/ocr` | Process vital signs OCR |

### Medication (`/medication`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/save-medication-log` | Save medication |
| GET | `/get-medication-history/<patient_id>` | Get medication history |
| POST | `/upload-prescription` | Upload prescription |
| POST | `/process-prescription-document` | OCR prescription |

### Appointments (`/appointments`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patient/appointments` | Get patient appointments |
| POST | `/patient/appointments` | Create appointment |
| PUT | `/patient/appointments/<id>` | Update appointment |
| DELETE | `/patient/appointments/<id>` | Cancel appointment |

---

## 🔒 Authentication

### JWT Token Flow

1. **Login**: POST `/auth/login`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "patient_id": "123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

2. **Use Token**: Include in headers
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Protected Routes

All routes except `/auth/signup`, `/auth/login`, `/auth/send-otp`, `/auth/verify-otp` require authentication.

---

## 💾 Database

### MongoDB Collections

- `patients` - User profiles
- `pregnancy_info` - Pregnancy tracking
- `symptoms` - Symptom records
- `vital_signs` - Vital sign measurements
- `medications` - Medication logs
- `prescriptions` - Prescription details
- `appointments` - Appointment bookings
- `mental_health_assessments` - Mental health data
- `user_activities` - Activity tracking

---

## 🧪 Testing

### Manual Testing with Postman/cURL

```bash
# Test signup
curl -X POST http://localhost:5001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "mobile": "+1234567890"
  }'

# Test login
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Test protected endpoint
curl -X GET http://localhost:5001/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🚀 Deployment

### Environment Variables for Production

```env
# Production MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DB_NAME=patient_alert_prod

# Strong JWT Secret
JWT_SECRET_KEY=generate-a-very-long-random-string-here

# Production Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourapp.com
SENDER_PASSWORD=app-specific-password

# CORS Settings
CORS_ORIGINS=https://yourfrontend.com,https://app.yourfrontend.com
```

### Production Checklist

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Use production MongoDB (Atlas)
- [ ] Enable CORS for specific origins only
- [ ] Set up SSL/TLS certificates
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Enable rate limiting
- [ ] Set up backups
- [ ] Configure reverse proxy (Nginx)

---

## 📝 API Documentation

### Swagger/OpenAPI

Access interactive API docs at:
```
http://localhost:5001/api/docs
```

(Note: You'll need to add flask-swagger-ui for this)

---

## 🤝 Support

For issues and questions:
- Check the documentation
- Review error logs in console
- Check MongoDB connection
- Verify environment variables

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🔄 Migrating to FastAPI

This application also has a **FastAPI** version available. To use FastAPI:

```bash
# Run FastAPI version
python run_fastapi_app.py

# Server runs on http://localhost:5003
```

See `README_FASTAPI.md` for FastAPI-specific documentation.

---

**Version:** 1.0.0 (Flask)  
**Last Updated:** October 2024  
**Framework:** Flask 3.0.3  
**Python:** 3.8+

