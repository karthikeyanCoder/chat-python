"""
Database Model - Handles all database operations
"""

import pymongo
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import logging

class Database:
    """Database connection and operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.patients_collection = None
        self.doctors_collection = None
        self.doctor_availability_collection = None
        self.is_connected = False
       
    def connect(self, max_retries=3):
        """Connect to MongoDB with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"[INFO] Connection attempt {attempt + 1}/{max_retries}")
                # Get MongoDB URI from environment
                mongodb_uri = os.environ.get('MONGO_URI')
                database_name = os.environ.get('DB_NAME')
                
                print(f"[INFO] Attempting to connect to MongoDB...")
                print(f"[INFO] URI: {mongodb_uri}")
                print(f"[INFO] Database: {database_name}")
                print(f"[INFO] Environment: {'Production' if 'render' in str(mongodb_uri).lower() else 'Development'}")
                
                # Create MongoDB client with better connection parameters
                self.client = MongoClient(
                    mongodb_uri, 
                    serverSelectionTimeoutMS=60000,  # 60 seconds
                    connectTimeoutMS=60000,          # 60 seconds
                    socketTimeoutMS=60000,           # 60 seconds
                    retryWrites=True,
                    retryReads=True,
                    maxPoolSize=10,
                    minPoolSize=1,
                    heartbeatFrequencyMS=10000,      # Send heartbeats every 10 seconds
                    maxIdleTimeMS=45000             # Close connections after 45s idle
                )
                
                # Test connection
                self.client.admin.command('ping')
                print("[SUCCESS] MongoDB connection test successful")
                
                # Get database
                self.db = self.client[database_name]
                print(f"[SUCCESS] Database '{database_name}' accessed successfully")
                
                # Initialize collections
                self._initialize_collections()
                
                # Create indexes
                self._create_indexes()
                
                self.is_connected = True
                print("[SUCCESS] Connected to MongoDB successfully")
                return True
                
            except Exception as e:
                print(f"[ERROR] MongoDB connection failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"[INFO] Waiting 5 seconds before retry...")
                    import time
                    time.sleep(5)
                else:
                    print("[INFO] Troubleshooting tips:")
                    print("   1. Check your internet connection")
                    print("   2. Verify MongoDB Atlas cluster is running")
                    print("   3. Check if your IP is whitelisted in MongoDB Atlas")
                    print("   4. Verify the connection string is correct")
                    print("   5. Try restarting your MongoDB Atlas cluster")
                    self.is_connected = False
                    return False
    
    def _initialize_collections(self):
        """Initialize collections from environment variables"""
        try:
            print("[INFO] Initializing collections from environment variables...")
            
            # Get collection names from environment variables (required)
            patients_collection_name = os.environ.get('PATIENTS_COLLECTION')
            doctors_collection_name = os.environ.get('DOCTORS_COLLECTION')
            
            # Validate required collections
            if not patients_collection_name:
                raise ValueError("PATIENTS_COLLECTION environment variable is required")
            
            if not doctors_collection_name:
                raise ValueError("DOCTORS_COLLECTION environment variable is required")
            
            # Initialize Patients collection
            self.patients_collection = self.db[patients_collection_name]
            print(f"[SUCCESS] Patients collection: {patients_collection_name}")
            
            # Initialize Doctors collection
            self.doctors_collection = self.db[doctors_collection_name]
            print(f"[SUCCESS] Doctors collection: {doctors_collection_name}")
            
            # Initialize temporary OTP collection
            self.temp_otp_collection = self.db['temp_otp']
            print(f"[SUCCESS] Temp OTP collection: temp_otp")
            
            # Initialize Doctor Availability collection
            self.doctor_availability_collection = self.db['doctor_availability']
            print(f"✅ Doctor availability collection: doctor_availability")
            
            print("✅ All collections initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Collection initialization failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for patients and doctors collections"""
        try:
            print("[INFO] Creating indexes...")
            
            # Patient indexes
            if self.patients_collection is not None:
                try:
                    self.patients_collection.create_index("patient_id", unique=True)
                    print("[SUCCESS] patient_id index created")
                except Exception as e:
                    print(f"[WARNING] patient_id index: {e}")
                
                try:
                    self.patients_collection.create_index("email", unique=True, sparse=True)
                    print("[SUCCESS] patient email index created")
                except Exception as e:
                    print(f"[WARNING] patient email index: {e}")
                
                try:
                    self.patients_collection.create_index("doctor_id")
                    print("[SUCCESS] patient doctor_id index created")
                except Exception as e:
                    print(f"[WARNING] patient doctor_id index: {e}")
            
            # Doctor indexes
            if self.doctors_collection is not None:
                try:
                    self.doctors_collection.create_index("doctor_id", unique=True)
                    print("[SUCCESS] doctor_id index created")
                except Exception as e:
                    print(f"[WARNING] doctor_id index: {e}")
                
                try:
                    self.doctors_collection.create_index("email", unique=True, sparse=True)
                    print("✅ doctor email index created")
                except Exception as e:
                    print(f"⚠️ doctor email index: {e}")
            
            # Doctor Availability indexes
            if self.doctor_availability_collection is not None:
                try:
                    self.doctor_availability_collection.create_index([
                        ('doctor_id', 1), ('date', 1)
                    ], name='doctor_date_index')
                    print("✅ doctor availability doctor_date index created")
                except Exception as e:
                    print(f"⚠️ doctor availability doctor_date index: {e}")
                
                try:
                    self.doctor_availability_collection.create_index([
                        ('doctor_id', 1), ('date', 1), ('types.type', 1)
                    ], name='doctor_date_type_index')
                    print("✅ doctor availability doctor_date_type index created")
                except Exception as e:
                    print(f"⚠️ doctor availability doctor_date_type index: {e}")
                
                try:
                    self.doctor_availability_collection.create_index([
                        ('doctor_id', 1), ('date', 1), ('types.slots.slot_id', 1)
                    ], name='doctor_date_slot_index')
                    print("✅ doctor availability doctor_date_slot index created")
                except Exception as e:
                    print(f"⚠️ doctor availability doctor_date_slot index: {e}")
                
                try:
                    self.doctor_availability_collection.create_index([
                        ('doctor_id', 1), ('is_active', 1)
                    ], name='doctor_active_index')
                    print("✅ doctor availability doctor_active index created")
                except Exception as e:
                    print(f"⚠️ doctor availability doctor_active index: {e}")
            
            print("[SUCCESS] All indexes created successfully")
            
        except Exception as e:
            print(f"[ERROR] Index creation failed: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.is_connected = False
            print("[SUCCESS] Disconnected from MongoDB")
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        if not self.is_connected:
            raise Exception("Database not connected")
        
        return self.db[collection_name]
    
    def is_healthy(self):
        """Check if database is healthy"""
        try:
            if not self.is_connected or not self.client:
                return False
            
            # Ping the database
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def get_upcoming_appointments(self, hours_ahead=24):
        """
        Get appointments that are within the specified hours ahead
        This method is used by the scheduler to find appointments needing reminders
        
        Args:
            hours_ahead: Number of hours ahead to look for appointments
        
        Returns:
            List of appointments with patient and doctor info
        """
        try:
            appointments = []
            
            # Calculate target datetime (current time + hours_ahead)
            target_datetime = datetime.utcnow() + timedelta(hours=hours_ahead)
            
            # Query patients with upcoming appointments
            pipeline = [
                # Match patients with appointments
                {
                    '$match': {
                        'appointments': {'$exists': True, '$ne': []}
                    }
                },
                # Unwind appointments array
                {'$unwind': '$appointments'},
                # Match appointments in the time window and not yet reminded
                {
                    '$match': {
                        'appointments.appointment_date': {'$exists': True},
                        'appointments.appointment_time': {'$exists': True},
                        'appointments.reminder_sent': {'$ne': True},
                        'appointments.appointment_status': {
                            '$in': ['scheduled', 'confirmed']
                        }
                    }
                },
                # Project only needed fields
                {
                    '$project': {
                        'patient_id': 1,
                        'patient_name': {'$concat': ['$first_name', ' ', '$last_name']},
                        'patient_email': '$email',
                        'appointment': '$appointments'
                    }
                }
            ]
            
            patients_with_appointments = list(self.patients_collection.aggregate(pipeline))
            
            # Process each appointment
            for item in patients_with_appointments:
                appointment = item['appointment']
                
                # Get doctor information
                doctor_id = appointment.get('doctor_id')
                doctor_name = "Unknown Doctor"
                
                if doctor_id:
                    doctor = self.doctors_collection.find_one({'doctor_id': doctor_id})
                    if doctor:
                        # Extract doctor name
                        if 'personal_info' in doctor:
                            first_name = doctor['personal_info'].get('first_name', '')
                            last_name = doctor['personal_info'].get('last_name', '')
                            doctor_name = f"Dr. {first_name} {last_name}".strip()
                        elif 'name' in doctor:
                            doctor_name = doctor['name']
                
                # Check if appointment is within time window
                appointment_datetime = self._parse_appointment_datetime(
                    appointment.get('appointment_date'),
                    appointment.get('appointment_time')
                )
                
                if appointment_datetime and appointment_datetime <= target_datetime:
                    appointments.append({
                        'patient_id': item['patient_id'],
                        'patient_name': item.get('patient_name', 'Unknown Patient'),
                        'patient_email': item.get('patient_email'),
                        'doctor_id': doctor_id,
                        'doctor_name': doctor_name,
                        'appointment_id': appointment.get('appointment_id'),
                        'appointment_date': appointment.get('appointment_date'),
                        'appointment_time': appointment.get('appointment_time'),
                        'appointment_type': appointment.get('appointment_type', 'Consultation'),
                        'appointment_status': appointment.get('appointment_status'),
                        'reminder_sent': appointment.get('reminder_sent', False)
                    })
            
            return appointments
            
        except Exception as e:
            logging.error(f"Error getting upcoming appointments: {str(e)}")
            return []
    
    def _parse_appointment_datetime(self, appointment_date: str, appointment_time: str):
        """
        Parse appointment date and time into datetime object
        
        Args:
            appointment_date: Date string in format YYYY-MM-DD
            appointment_time: Time string in format HH:MM
        
        Returns:
            datetime object or None
        """
        try:
            if not appointment_date or not appointment_time:
                return None
            
            # Parse date
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
            
            # Parse time
            time_parts = appointment_time.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            # Combine date and time
            appointment_datetime = date_obj.replace(hour=hour, minute=minute)
            
            return appointment_datetime
            
        except Exception as e:
            logging.error(f"Error parsing appointment datetime: {str(e)}")
            return None
