"""
Doctor Controller - Handles doctor operations
"""

from flask import request, jsonify
from typing import Dict, Any
from datetime import datetime, timedelta
import sys
import os
import json

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.objectid_converter import convert_objectid_to_string

# Import RAG services
try:
    from services.rag_medical_service import RAGMedicalService
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG services not available. AI summaries will use basic mode.")

class DoctorController:
    """Doctor controller"""
    
    def __init__(self, doctor_model, jwt_service, validators):
        self.doctor_model = doctor_model
        self.jwt_service = jwt_service
        self.validators = validators
    
        # Initialize RAG service if available
        if RAG_AVAILABLE:
            try:
                self.rag_service = RAGMedicalService()
                print("✅ RAG Medical Service initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize RAG service: {str(e)}")
                self.rag_service = None
        else:
            self.rag_service = None
    
    def get_profile(self, doctor_id: str) -> tuple:
        """Get doctor profile"""
        try:
            if not doctor_id:
                return jsonify({'error': 'Doctor ID is required'}), 400
            
            doctor = self.doctor_model.get_doctor_by_id(doctor_id)
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            return jsonify({
                'success': True,
                'doctor': doctor
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def update_profile(self, doctor_id: str, request) -> tuple:
        """Update doctor profile"""
        try:
            if not doctor_id:
                return jsonify({'error': 'Doctor ID is required'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Update doctor profile
            result = self.doctor_model.update_doctor_profile(doctor_id, data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def delete_profile(self, doctor_id: str) -> tuple:
        """Delete doctor profile (soft delete)"""
        try:
            if not doctor_id:
                return jsonify({'error': 'Doctor ID is required'}), 400
            
            # Soft delete by setting status to 'deleted'
            result = self.doctor_model.update_doctor_profile(doctor_id, {'status': 'deleted'})
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Doctor profile deleted successfully'
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def complete_profile(self, request) -> tuple:
        """Complete doctor profile"""
        try:
            data = request.get_json()
            doctor_id = data.get('doctor_id', '').strip()
            
            if not doctor_id:
                return jsonify({'error': 'Doctor ID is required'}), 400
            
            # Complete doctor profile
            result = self.doctor_model.complete_doctor_profile(doctor_id, data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_all_doctors(self, request) -> tuple:
        """Get all doctors list with patient count for patient selection"""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            search = request.args.get('search', '').strip()
            specialization = request.args.get('specialization', '').strip()
            city = request.args.get('city', '').strip()
            min_patients = request.args.get('min_patients', '').strip()
            
            # Build query filter
            query_filter = {"status": {"$ne": "deleted"}}
            
            if search:
                query_filter["$or"] = [
                    {"username": {"$regex": search, "$options": "i"}},
                    {"first_name": {"$regex": search, "$options": "i"}},
                    {"last_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                    {"specialization": {"$regex": search, "$options": "i"}}
                ]
            
            if specialization:
                query_filter["specialization"] = {"$regex": specialization, "$options": "i"}
                
            if city:
                query_filter["city"] = {"$regex": city, "$options": "i"}
            
            # Get doctors from database
            result = self.doctor_model.get_all_doctors(
                query_filter=query_filter,
                page=page,
                limit=limit
            )
            
            if result['success']:
                # Filter by minimum patients if specified
                doctors = result['doctors']
                if min_patients and min_patients.isdigit():
                    min_count = int(min_patients)
                    doctors = [doc for doc in doctors if doc.get('patient_count', 0) >= min_count]
                
                return jsonify({
                    'success': True,
                    'doctors': doctors,
                    'total_count': result['total_count'],
                    'page': page,
                    'limit': limit,
                    'total_pages': result['total_pages'],
                    'filters_applied': {
                        'search': search,
                        'specialization': specialization,
                        'city': city,
                        'min_patients': min_patients
                    }
                }), 200
            else:
                return jsonify({'error': result['error']}), 500
            
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_public_doctor_profile(self, doctor_id: str) -> tuple:
        """Get public doctor profile for patient selection"""
        try:
            if not doctor_id:
                return jsonify({'error': 'Doctor ID is required'}), 400
            
            doctor = self.doctor_model.get_doctor_by_id(doctor_id)
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            # Get patient count
            patient_count = self.doctor_model._count_patients_for_doctor(doctor_id)
            
            # Prepare public profile (exclude sensitive data)
            public_profile = {
                'doctor_id': doctor.get('doctor_id'),
                'username': doctor.get('username'),
                'first_name': doctor.get('first_name'),
                'last_name': doctor.get('last_name'),
                'specialization': doctor.get('specialization'),
                'experience_years': doctor.get('experience_years'),
                'license_number': doctor.get('license_number'),
                'hospital_name': doctor.get('hospital_name'),
                'address': doctor.get('address'),
                'city': doctor.get('city'),
                'state': doctor.get('state'),
                'pincode': doctor.get('pincode'),
                'consultation_fee': doctor.get('consultation_fee'),
                'languages': doctor.get('languages', []),
                'qualifications': doctor.get('qualifications', []),
                'patient_count': patient_count,
                'status': doctor.get('status'),
                'created_at': doctor.get('created_at'),
                'is_profile_complete': doctor.get('is_profile_complete')
            }
            
            return jsonify({
                'success': True,
                'doctor': public_profile
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_patients(self, request) -> tuple:
        """Get patients list for doctor"""
        try:
            # For doctor-only app, we don't need to validate doctor_id
            # Just get all patients from the database using the working logic from app_simple.py
            if hasattr(self.doctor_model, 'db') and hasattr(self.doctor_model.db, 'patients_collection'):
                patients_collection = self.doctor_model.db.patients_collection
                
                # Get all active patients (using the same logic as app_simple.py)
                patients = list(patients_collection.find(
                    {"status": {"$ne": "deleted"}},
                    {
                        "patient_id": 1,
                        "username": 1,
                        "email": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "date_of_birth": 1,
                        "blood_type": 1,
                        "mobile": 1,
                        "is_pregnant": 1,
                        "is_profile_complete": 1,
                        "created_at": 1,
                        "last_login": 1,
                        "status": 1,
                        "age": 1,
                        "gender": 1,
                        "address": 1,
                        "city": 1,
                        "state": 1,
                        "pincode": 1
                    }
                ))
                
                # Format patient data (using the same logic as app_simple.py)
                formatted_patients = []
                for patient in patients:
                    formatted_patients.append({
                        "patient_id": patient.get("patient_id", ""),
                        "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown'),
                        "email": patient.get("email", ""),
                        "mobile": patient.get("mobile", ""),
                        "blood_type": patient.get("blood_type", ""),
                        "date_of_birth": patient.get("date_of_birth", ""),
                        "age": patient.get("age", 0),
                        "gender": patient.get("gender", ""),
                        "is_pregnant": patient.get("is_pregnant", False),
                        "is_profile_complete": patient.get("is_profile_complete", False),
                        "status": patient.get("status", "active"),
                        "created_at": patient.get("created_at", ""),
                        "last_login": patient.get("last_login", ""),
                        "address": patient.get("address", ""),
                        "city": patient.get("city", ""),
                        "state": patient.get("state", ""),
                        "pincode": patient.get("pincode", ""),
                        "object_id": str(patient.get("_id", ""))
                    })
                
                return jsonify({
                    "patients": formatted_patients,
                    "total_count": len(formatted_patients),
                    "message": "Patients retrieved successfully"
                }), 200
            else:
                return jsonify({'error': 'Database connection not available'}), 500

        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_patient_details(self, request, patient_id: str) -> tuple:
        """Get detailed patient information for doctor"""
        try:
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            mental_health_collection = self.doctor_model.db.mental_health_collection
            
            # Find patient by patient_id or object_id
            from bson import ObjectId
            patient = patients_collection.find_one({
                "$or": [
                    {"patient_id": patient_id},
                    {"_id": ObjectId(patient_id) if ObjectId.is_valid(patient_id) else None}
                ]
            })
            
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            # Get patient's mental health logs
            mental_health_logs = list(mental_health_collection.find(
                {"patient_id": patient.get("patient_id")},
                {"_id": 0}
            ).sort("date", -1).limit(10))
            
            # Format patient details
            patient_details = {
                "patient_id": patient.get("patient_id", ""),
                "username": patient.get("username", ""),
                "email": patient.get("email", ""),
                "first_name": patient.get("first_name", ""),
                "last_name": patient.get("last_name", ""),
                "full_name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown'),
                "date_of_birth": patient.get("date_of_birth", ""),
                "blood_type": patient.get("blood_type", ""),
                "mobile": patient.get("mobile", ""),
                "address": patient.get("address", ""),
                "emergency_contact": patient.get("emergency_contact", ""),
                "is_pregnant": patient.get("is_pregnant", False),
                "pregnancy_due_date": patient.get("pregnancy_due_date", ""),
                "is_profile_complete": patient.get("is_profile_complete", False),
                "status": patient.get("status", "active"),
                "created_at": patient.get("created_at", ""),
                "last_login": patient.get("last_login", ""),
                "medical_history": patient.get("medical_history", []),
                "allergies": patient.get("allergies", []),
                "current_medications": patient.get("current_medications", []),
                "mental_health_logs": mental_health_logs,
                "object_id": str(patient.get("_id", ""))
            }
            
            return jsonify({
                "patient": patient_details,
                "message": "Patient details retrieved successfully"
            }), 200
            
        except Exception as e:
            print(f"❌ Error retrieving patient details: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500

    def get_patient_full_details(self, request, patient_id: str) -> tuple:
        """Get complete patient details with all health data in one call"""
        try:
            print(f"🔍 Getting FULL patient details for ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Convert all ObjectIds to strings recursively
            patient = convert_objectid_to_string(patient)
            
            # Get all health data from patient document
            # Handle both full_name and first_name/last_name combinations
            full_name = patient.get('full_name', '')
            if not full_name:
                first_name = patient.get('first_name', '')
                last_name = patient.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
            
            full_details = {
                'success': True,
                'patient_id': patient_id,
                'patient_info': {
                    'full_name': full_name,
                    'first_name': patient.get('first_name', ''),
                    'last_name': patient.get('last_name', ''),
                    'username': patient.get('username', ''),
                    'email': patient.get('email', ''),
                    'mobile': patient.get('mobile', '') or patient.get('phone', ''),
                    'age': patient.get('age', 0),
                    'blood_type': patient.get('blood_type', ''),
                    'gender': patient.get('gender', ''),
                    'is_pregnant': patient.get('is_pregnant', False),
                    'pregnancy_week': patient.get('pregnancy_week', 0),
                    'expected_delivery_date': patient.get('expected_delivery_date', ''),
                    'last_period_date': patient.get('last_period_date', '') or patient.get('last_menstrual_period', ''),
                    'last_menstrual_period': patient.get('last_period_date', '') or patient.get('last_menstrual_period', ''),
                    'height': patient.get('height', ''),
                    'weight': patient.get('weight', ''),
                    'status': patient.get('status', 'active'),
                    'created_at': patient.get('created_at', ''),
                    'address': patient.get('address', ''),
                    'city': patient.get('city', ''),
                    'state': patient.get('state', ''),
                    'pincode': patient.get('pincode', ''),
                    'date_of_birth': patient.get('date_of_birth', ''),
                    'emergency_contact': patient.get('emergency_contact', {}),
                    'emergency_contact_phone': patient.get('emergency_contact_phone', ''),
                    'medical_history': patient.get('medical_history', []),
                    'allergies': patient.get('allergies', []),
                    'current_medications': patient.get('current_medications', [])
                },
                'health_data': {
                    'medication_logs': patient.get('medication_logs', []),
                    'symptom_analysis_reports': patient.get('symptom_analysis_reports', []),
                    'food_data': patient.get('food_data', []),
                    'tablet_logs': patient.get('tablet_logs', []),
                    'kick_logs': patient.get('kick_logs', []),
                    'kick_count_logs': patient.get('kick_count_logs', []),
                    'sleep_logs': patient.get('sleep_logs', []),
                    'mental_health_logs': patient.get('mental_health_logs', []),
                    'hydration_records': patient.get('hydration_records', []),
                    'hydration_goal': patient.get('hydration_goal', {}),
                    'prescription_documents': patient.get('prescription_documents', []),
                    'vital_signs_logs': patient.get('vital_signs_logs', []),
                    'appointments': patient.get('appointments', [])
                },
                'summary': {
                    'total_medications': len(patient.get('medication_logs', [])),
                    'total_symptoms': len(patient.get('symptom_analysis_reports', [])),
                    'total_food_entries': len(patient.get('food_data', [])),
                    'total_tablet_logs': len(patient.get('tablet_logs', [])),
                    'total_kick_logs': len(patient.get('kick_logs', [])),
                    'total_kick_count_logs': len(patient.get('kick_count_logs', [])),
                    'total_sleep_logs': len(patient.get('sleep_logs', [])),
                    'total_mental_health': len(patient.get('mental_health_logs', [])),
                    'total_hydration_records': len(patient.get('hydration_records', [])),
                    'total_prescriptions': len(patient.get('prescription_documents', [])),
                    'total_vital_signs': len(patient.get('vital_signs_logs', [])),
                    'total_appointments': len(patient.get('appointments', []))
                }
            }
            
            # Convert all ObjectIds in the full_details recursively
            full_details = convert_objectid_to_string(full_details)
            
            print(f"✅ Retrieved FULL patient details for: {patient_id}")
            print(f"📊 Summary: {full_details['summary']}")
            
            return jsonify(full_details), 200
            
        except Exception as e:
            print(f"Error getting full patient details: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    # ==================== AI SUMMARY WITH RISK ASSESSMENT HELPER METHODS ====================
    
    def _filter_data_by_date_range(self, data_array, days=None, start_date=None, end_date=None):
        """Filter data array by date range
        
        Args:
            data_array: Array of data items to filter
            days: Number of days from now (if start_date/end_date not provided)
            start_date: Start date (datetime object) for custom range
            end_date: End date (datetime object) for custom range
        
        Returns:
            Filtered data array
        """
        if not data_array:
            return data_array
        
        try:
            # Determine date range mode
            if start_date and end_date:
                # Custom date range mode
                cutoff_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff_end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                print(f"   🗓️  Custom range: {cutoff_start.strftime('%Y-%m-%d')} to {cutoff_end.strftime('%Y-%m-%d')}")
            elif days:
                # Days from now mode
                cutoff_start = datetime.now() - timedelta(days=days)
                cutoff_end = datetime.now()
            else:
                # No filtering
                return data_array
            
            filtered_data = []
            
            for item in data_array:
                item_date = None
                
                # Try different date field names
                for date_field in ['timestamp', 'date', 'created_at', 'createdAt', 'takenAt', 'sessionStartTime', 'startTime']:
                    if date_field in item and item[date_field]:
                        try:
                            # Handle ISO string dates
                            if isinstance(item[date_field], str):
                                # Remove 'Z' and parse as ISO format
                                date_str = item[date_field].replace('Z', '+00:00')
                                item_date = datetime.fromisoformat(date_str)
                            elif isinstance(item[date_field], datetime):
                                item_date = item[date_field]
                            break
                        except Exception as parse_error:
                            # Try alternative parsing
                            try:
                                if isinstance(item[date_field], str):
                                    # Try YYYY-MM-DD format
                                    item_date = datetime.strptime(item[date_field][:10], '%Y-%m-%d')
                            except:
                                continue
                
                # If date found and within range, include it
                if item_date:
                    if cutoff_start <= item_date <= cutoff_end:
                        filtered_data.append(item)
                else:
                    # Include items without dates (better than excluding)
                    filtered_data.append(item)
            
            print(f"   ✅ Filtered: {len(filtered_data)}/{len(data_array)} items")
            return filtered_data
            
        except Exception as e:
            print(f"❌ Error filtering data by date: {e}")
            import traceback
            traceback.print_exc()
            return data_array
    
    def _calculate_pregnancy_risk_score(self, patient_info, statistics):
        """Calculate pregnancy risk score (0-100) and identify risk factors"""
        risk_score = 0
        risk_factors = []
        protective_factors = []
        red_flags = []
        
        # Basic Risk Factors - Maternal Age
        age = patient_info.get('age', 25)
        if age and age < 18:
            risk_score += 15
            risk_factors.append({
                'factor': 'Maternal age under 18',
                'severity': 'Major',
                'impact': 'High',
                'notes': 'Increased risk for complications in adolescent pregnancy'
            })
        elif age and age > 35:
            risk_score += 10
            risk_factors.append({
                'factor': 'Advanced maternal age (>35)',
                'severity': 'Moderate',
                'impact': 'Medium',
                'notes': 'Slightly increased risk, requires closer monitoring'
            })
        else:
            if age:
                protective_factors.append(f"Maternal age {age} is within optimal range (18-35)")
        
        # Medication Adherence
        med_adherence = statistics.get('medication_adherence', {}).get('adherence_rate', 100)
        if med_adherence < 50:
            risk_score += 20
            risk_factors.append({
                'factor': 'Poor medication adherence',
                'severity': 'Major',
                'impact': 'High',
                'notes': f'Only {med_adherence:.1f}% adherence rate'
            })
            red_flags.append(f"Critical: Medication adherence at {med_adherence:.1f}%")
        elif med_adherence < 80:
            risk_score += 10
            risk_factors.append({
                'factor': 'Below optimal medication adherence',
                'severity': 'Moderate',
                'impact': 'Medium',
                'notes': f'{med_adherence:.1f}% adherence rate'
            })
        else:
            protective_factors.append(f"Excellent medication adherence ({med_adherence:.1f}%)")
        
        # Symptom Severity
        symptoms_stats = statistics.get('symptoms_tracking', {})
        severe_count = symptoms_stats.get('severity_breakdown', {}).get('severe', 0)
        if severe_count > 0:
            risk_score += 15
            risk_factors.append({
                'factor': 'Severe symptoms reported',
                'severity': 'Major',
                'impact': 'High',
                'notes': f'{severe_count} severe symptom reports'
            })
            red_flags.append(f"Alert: {severe_count} severe symptoms require attention")
        
        # Sleep Deprivation
        sleep_avg = statistics.get('sleep_patterns', {}).get('average_duration_hours', 7)
        if sleep_avg > 0 and sleep_avg < 5:
            risk_score += 15
            risk_factors.append({
                'factor': 'Severe sleep deprivation',
                'severity': 'Major',
                'impact': 'High',
                'notes': f'Average {sleep_avg:.1f} hours per night'
            })
        elif sleep_avg > 0 and sleep_avg < 6:
            risk_score += 8
            risk_factors.append({
                'factor': 'Sleep deprivation',
                'severity': 'Moderate',
                'impact': 'Medium',
                'notes': f'Average {sleep_avg:.1f} hours, recommended 7-9 hours'
            })
        elif sleep_avg >= 7:
            protective_factors.append(f"Good sleep duration ({sleep_avg:.1f} hours average)")
        
        # Hydration
        hydration_goal = statistics.get('hydration', {}).get('goal_achievement_rate', 100)
        if hydration_goal < 50:
            risk_score += 10
            risk_factors.append({
                'factor': 'Poor hydration',
                'severity': 'Moderate',
                'impact': 'Medium',
                'notes': f'Only {hydration_goal:.1f}% of hydration goal met'
            })
        elif hydration_goal >= 80:
            protective_factors.append(f"Good hydration habits ({hydration_goal:.1f}% goal achievement)")
        
        # Mental Health
        mental_health = statistics.get('mental_health', {})
        anxiety_avg = mental_health.get('anxiety_level_average', 0)
        stress_avg = mental_health.get('stress_level_average', 0)
        
        if anxiety_avg > 7 or stress_avg > 7:
            risk_score += 12
            risk_factors.append({
                'factor': 'Elevated anxiety or stress levels',
                'severity': 'Moderate',
                'impact': 'Medium',
                'notes': f'Anxiety: {anxiety_avg:.1f}/10, Stress: {stress_avg:.1f}/10'
            })
        elif anxiety_avg > 0 and anxiety_avg <= 4 and stress_avg > 0 and stress_avg <= 4:
            protective_factors.append("Good mental health indicators")
        
        # Nutrition
        food_stats = statistics.get('food_nutrition', {})
        coverage = food_stats.get('coverage_percentage', 0)
        if coverage < 30:
            risk_score += 8
            risk_factors.append({
                'factor': 'Insufficient nutrition tracking',
                'severity': 'Minor',
                'impact': 'Low',
                'notes': f'Only {coverage:.1f}% of days with food logs'
            })
        elif coverage >= 70:
            protective_factors.append(f"Good nutrition tracking ({coverage:.1f}% coverage)")
        
        # Kick Count Monitoring (Fetal Movement)
        kick_stats = statistics.get('kick_count_tracking', {})
        kick_sessions = kick_stats.get('sessions_in_range', 0)
        pregnancy_week = patient_info.get('pregnancy_week', 0)
        is_pregnant = patient_info.get('is_pregnant', False)
        
        if is_pregnant and pregnancy_week >= 28:  # Should monitor kicks after week 28
            if kick_sessions == 0:
                risk_score += 15
                risk_factors.append({
                    'factor': 'No fetal movement tracking',
                    'severity': 'Major',
                    'impact': 'High',
                    'notes': f'At week {pregnancy_week}, kick count monitoring is recommended'
                })
                red_flags.append(f"Important: No kick count monitoring at week {pregnancy_week}")
            elif kick_sessions > 5:
                protective_factors.append("Regular fetal movement monitoring")
        
        # Determine risk level
        if risk_score <= 30:
            risk_level = "Low"
            risk_category = "Low Risk Pregnancy"
        elif risk_score <= 60:
            risk_level = "Moderate"
            risk_category = "Moderate Risk - Requires Monitoring"
        else:
            risk_level = "High"
            risk_category = "High Risk - Requires Close Medical Attention"
        
        return {
            'overall_risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'risk_category': risk_category,
            'risk_factors': risk_factors,
            'protective_factors': protective_factors,
            'red_flags': red_flags,
            'requires_immediate_attention': len(red_flags) > 0 or risk_score > 70
        }
    
    def _calculate_comprehensive_statistics(self, health_data, summary, days):
        """Calculate comprehensive statistics for all data categories"""
        
        # Data Collection Overview
        total_data_points = (
            len(health_data.get('food_data', [])) +
            len(health_data.get('medication_history', [])) +
            len(health_data.get('symptom_analysis_reports', [])) +
            len(health_data.get('mental_health_logs', [])) +
            len(health_data.get('kick_count_logs', [])) +
            len(health_data.get('hydration_records', []))
        )
        
        # Food/Nutrition Statistics
        food_data = health_data.get('food_data', [])
        days_with_food = len(set([self._extract_date_from_item(item) for item in food_data if self._extract_date_from_item(item)]))
        
        food_stats = {
            'total_entries': len(food_data),
            'entries_in_range': len(food_data),
            'average_per_day': round(len(food_data) / days, 2) if days > 0 else 0,
            'last_entry': food_data[0].get('timestamp', 'N/A') if food_data else 'N/A',
            'days_with_entries': days_with_food,
            'coverage_percentage': round((days_with_food / days * 100), 1) if days > 0 else 0
        }
        
        # Medication Adherence Statistics
        medication_history = health_data.get('medication_history', [])
        total_medications = summary.get('total_medications', 0)
        
        # Estimate adherence based on medication logs
        total_expected_doses = days  # Assuming 1 dose per day minimum
        adherence_rate = (len(medication_history) / total_expected_doses * 100) if total_expected_doses > 0 else 100
        
        med_stats = {
            'total_logs': len(medication_history),
            'logs_in_range': len(medication_history),
            'prescribed_medications': total_medications,
            'adherence_rate': round(min(adherence_rate, 100), 1),
            'missed_doses': max(total_expected_doses - len(medication_history), 0),
            'on_time_percentage': 90.0,  # Default assumption
            'active_prescriptions': health_data.get('prescription_documents', [])[:5]
        }
        
        # Symptoms Tracking Statistics
        symptoms = health_data.get('symptom_analysis_reports', [])
        severity_breakdown = {'mild': 0, 'moderate': 0, 'severe': 0}
        symptom_counts = {}
        
        for symptom in symptoms:
            severity = symptom.get('severity', 'mild').lower()
            if severity in severity_breakdown:
                severity_breakdown[severity] += 1
            
            symptom_text = symptom.get('symptom_text', 'Unknown')
            symptom_counts[symptom_text] = symptom_counts.get(symptom_text, 0) + 1
        
        most_common = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        symptom_stats = {
            'total_reports': len(symptoms),
            'reports_in_range': len(symptoms),
            'unique_symptoms': len(symptom_counts),
            'severity_breakdown': severity_breakdown,
            'most_common_symptoms': [{'symptom': s[0], 'count': s[1]} for s in most_common],
            'last_report': symptoms[0].get('timestamp', 'N/A') if symptoms else 'N/A'
        }
        
        # Sleep Patterns Statistics
        sleep_logs = health_data.get('sleep_logs', [])
        sleep_durations = []
        
        for log in sleep_logs:
            # Extract duration from totalSleep field (e.g., "8 hours")
            total_sleep = log.get('totalSleep', '0 hours')
            try:
                duration = float(total_sleep.split()[0])
                sleep_durations.append(duration)
            except:
                pass
        
        sleep_stats = {
            'total_logs': len(sleep_logs),
            'logs_in_range': len(sleep_logs),
            'average_duration_hours': round(sum(sleep_durations) / len(sleep_durations), 1) if sleep_durations else 0,
            'average_quality_score': 0,
            'best_sleep_duration': max(sleep_durations) if sleep_durations else 0,
            'worst_sleep_duration': min(sleep_durations) if sleep_durations else 0,
            'nights_with_disturbances': 0,
            'sleep_consistency_score': round(100 - (self._calculate_std_dev(sleep_durations) * 10), 0) if len(sleep_durations) > 1 else 100
        }
        
        # Kick Count Tracking Statistics
        kick_logs = health_data.get('kick_count_logs', [])
        kick_counts = [log.get('kickCount', 0) for log in kick_logs if log.get('kickCount')]
        session_durations = [log.get('sessionDuration', 0) for log in kick_logs if log.get('sessionDuration')]
        
        kick_stats = {
            'total_sessions': len(kick_logs),
            'sessions_in_range': len(kick_logs),
            'average_kicks_per_session': round(sum(kick_counts) / len(kick_counts), 0) if kick_counts else 0,
            'average_session_duration_minutes': round(sum(session_durations) / len(session_durations), 0) if session_durations else 0,
            'kicks_per_hour_average': round((sum(kick_counts) / sum(session_durations) * 60), 0) if sum(session_durations) > 0 else 0,
            'last_session': kick_logs[0].get('timestamp', 'N/A') if kick_logs else 'N/A',
            'movement_pattern': 'Normal and consistent' if len(kick_logs) > 5 else 'Limited data'
        }
        
        # Mental Health Statistics
        mental_logs = health_data.get('mental_health_logs', [])
        mood_scores = [log.get('mood_score', 0) for log in mental_logs if log.get('mood_score')]
        
        mental_stats = {
            'total_checkins': len(mental_logs),
            'checkins_in_range': len(mental_logs),
            'average_mood_score': round(sum(mood_scores) / len(mood_scores), 1) if mood_scores else 0,
            'anxiety_level_average': 0,
            'stress_level_average': 0,
            'mood_trend': 'Stable',
            'elevated_stress_days': 0,
            'support_sessions': 0
        }
        
        # Hydration Statistics
        hydration_records = health_data.get('hydration_records', [])
        hydration_goal_data = health_data.get('hydration_goal', {})
        intake_amounts = [record.get('amount_ml', 0) for record in hydration_records if record.get('amount_ml')]
        
        # Calculate daily totals by grouping by date
        daily_totals_dict = {}
        for record in hydration_records:
            date = self._extract_date_from_item(record)
            if date:
                amount = record.get('amount_ml', 0)
                daily_totals_dict[date] = daily_totals_dict.get(date, 0) + amount
        
        daily_totals = list(daily_totals_dict.values())
        goal_ml = hydration_goal_data.get('daily_goal_ml', 2000)
        days_met_goal = len([total for total in daily_totals if total >= goal_ml])
        
        hydration_stats = {
            'total_records': len(hydration_records),
            'records_in_range': len(hydration_records),
            'average_daily_intake_ml': round(sum(daily_totals) / len(daily_totals), 0) if daily_totals else 0,
            'goal_ml': goal_ml,
            'goal_achievement_rate': round((days_met_goal / len(daily_totals) * 100), 1) if daily_totals else 0,
            'days_met_goal': days_met_goal,
            'days_below_goal': len(daily_totals) - days_met_goal if daily_totals else 0,
            'highest_intake_ml': max(daily_totals) if daily_totals else 0,
            'lowest_intake_ml': min(daily_totals) if daily_totals else 0
        }
        
        return {
            'data_collection_overview': {
                'total_data_points': total_data_points,
                'date_range': f"{(datetime.now() - timedelta(days=days)).strftime('%b %d, %Y')} - {datetime.now().strftime('%b %d, %Y')}",
                'days_analyzed': days
            },
            'food_nutrition': food_stats,
            'medication_adherence': med_stats,
            'symptoms_tracking': symptom_stats,
            'sleep_patterns': sleep_stats,
            'kick_count_tracking': kick_stats,
            'mental_health': mental_stats,
            'hydration': hydration_stats
        }
    
    def _extract_date_from_item(self, item):
        """Extract date from item for counting unique days"""
        for field in ['timestamp', 'date', 'created_at', 'createdAt']:
            if field in item and item[field]:
                try:
                    if isinstance(item[field], str):
                        return item[field][:10]  # YYYY-MM-DD
                    elif isinstance(item[field], datetime):
                        return item[field].strftime('%Y-%m-%d')
                except:
                    continue
        return None
    
    def _calculate_std_dev(self, numbers):
        """Calculate standard deviation"""
        if len(numbers) < 2:
            return 0
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
        return variance ** 0.5
    
    def _calculate_trimester(self, pregnancy_week):
        """Calculate trimester from pregnancy week"""
        if not pregnancy_week or pregnancy_week <= 0:
            return 0
        if pregnancy_week <= 13:
            return 1
        elif pregnancy_week <= 26:
            return 2
        else:
            return 3

    def get_patient_ai_summary(self, request, patient_id: str) -> tuple:
        """Get comprehensive AI-powered medical summary with risk assessment for a patient
        
        Query Parameters:
        - days: Number of days to analyze (default: 30) - e.g., ?days=7
        - start_date: Start date in YYYY-MM-DD format - e.g., ?start_date=2025-10-01
        - end_date: End date in YYYY-MM-DD format - e.g., ?end_date=2025-10-15
        
        Note: If start_date and end_date are provided, they take precedence over days parameter
        """
        try:
            print(f"🤖 Getting comprehensive AI summary with risk assessment for patient: {patient_id}")
            
            # Get query parameters for date range
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            days_param = request.args.get('days', '30')
            
            # Validate and parse date parameters
            start_date = None
            end_date = None
            days = 30
            date_range_type = 'days'
            
            if start_date_str and end_date_str:
                # Use specific date range
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    
                    # Validate date range
                    if start_date > end_date:
                        return jsonify({
                            'success': False,
                            'message': 'start_date must be before or equal to end_date'
                        }), 400
                    
                    if end_date > datetime.now():
                        end_date = datetime.now()
                    
                    # Calculate days for statistics
                    days = (end_date - start_date).days + 1
                    date_range_type = 'custom'
                    
                    print(f"📅 Analyzing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({days} days)")
                    
                except ValueError as ve:
                    return jsonify({
                        'success': False,
                        'message': f'Invalid date format. Use YYYY-MM-DD format. Error: {str(ve)}'
                    }), 400
            elif start_date_str or end_date_str:
                # If only one date is provided, return error
                return jsonify({
                    'success': False,
                    'message': 'Both start_date and end_date must be provided together'
                }), 400
            else:
                # Use days parameter (default: 30)
                try:
                    days = int(days_param)
                    if days < 1:
                        return jsonify({
                            'success': False,
                            'message': 'days parameter must be a positive integer'
                        }), 400
                    if days > 365:
                        return jsonify({
                            'success': False,
                            'message': 'days parameter cannot exceed 365 days'
                        }), 400
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'days parameter must be a valid integer'
                    }), 400
                
                print(f"📅 Analyzing last {days} days of data")
            
            # First get the full patient details
            full_details_response = self.get_patient_full_details(request, patient_id)
            
            if full_details_response[1] != 200:  # Check status code
                return full_details_response
            
            patient_data = full_details_response[0].get_json()
            
            if not patient_data.get('success'):
                return jsonify({'success': False, 'message': 'Failed to get patient data'}), 400
            
            # Extract patient info and health data
            patient_info = patient_data.get('patient_info', {})
            health_data = patient_data.get('health_data', {})
            summary = patient_data.get('summary', {})
            
            # Filter health data by date range
            if date_range_type == 'custom':
                print(f"🔍 Filtering data by custom date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
                filtered_health_data = {
                    'food_data': self._filter_data_by_date_range(health_data.get('food_data', []), days, start_date, end_date),
                    'medication_history': self._filter_data_by_date_range(health_data.get('medication_logs', []), days, start_date, end_date),
                    'symptom_analysis_reports': self._filter_data_by_date_range(health_data.get('symptom_analysis_reports', []), days, start_date, end_date),
                    'mental_health_logs': self._filter_data_by_date_range(health_data.get('mental_health_logs', []), days, start_date, end_date),
                    'kick_count_logs': self._filter_data_by_date_range(health_data.get('kick_count_logs', []), days, start_date, end_date),
                    'sleep_logs': self._filter_data_by_date_range(health_data.get('sleep_logs', []), days, start_date, end_date),
                    'hydration_records': self._filter_data_by_date_range(health_data.get('hydration_records', []), days, start_date, end_date),
                    'hydration_goal': health_data.get('hydration_goal', {}),
                    'prescription_documents': health_data.get('prescription_documents', [])
                }
            else:
                print(f"🔍 Filtering data by last {days} days...")
                filtered_health_data = {
                    'food_data': self._filter_data_by_date_range(health_data.get('food_data', []), days),
                    'medication_history': self._filter_data_by_date_range(health_data.get('medication_logs', []), days),
                    'symptom_analysis_reports': self._filter_data_by_date_range(health_data.get('symptom_analysis_reports', []), days),
                    'mental_health_logs': self._filter_data_by_date_range(health_data.get('mental_health_logs', []), days),
                    'kick_count_logs': self._filter_data_by_date_range(health_data.get('kick_count_logs', []), days),
                    'sleep_logs': self._filter_data_by_date_range(health_data.get('sleep_logs', []), days),
                    'hydration_records': self._filter_data_by_date_range(health_data.get('hydration_records', []), days),
                    'hydration_goal': health_data.get('hydration_goal', {}),
                    'prescription_documents': health_data.get('prescription_documents', [])
                }
            
            # Calculate comprehensive statistics
            print(f"📊 Calculating comprehensive statistics...")
            statistics = self._calculate_comprehensive_statistics(filtered_health_data, summary, days)
            
            # Calculate pregnancy risk assessment
            print(f"🎯 Calculating pregnancy risk assessment...")
            risk_assessment = self._calculate_pregnancy_risk_score(patient_info, statistics)
            
            print(f"✅ Risk Level: {risk_assessment['overall_risk_level']} ({risk_assessment['risk_score']}/100)")
            
            # Prepare patient info with trimester
            pregnancy_week = patient_info.get('pregnancy_week', 0)
            expected_delivery_date = patient_info.get('expected_delivery_date', '') or patient_info.get('edd', '') or 'N/A'
            last_period = patient_info.get('last_period_date', '') or patient_info.get('last_menstrual_period', '') or 'N/A'
            
            patient_info_enhanced = {
                'fullname': patient_info.get('full_name', 'N/A'),
                'age': patient_info.get('age', 'N/A'),
                'pregnancy_week': pregnancy_week,
                'trimester': self._calculate_trimester(pregnancy_week),
                'is_pregnant': patient_info.get('is_pregnant', False),
                'expected_delivery_date': expected_delivery_date,
                'last_period_date': last_period,
                'last_menstrual_period': last_period,
                'height': patient_info.get('height', '') or 'N/A',
                'weight': patient_info.get('weight', '') or 'N/A',
                'blood_type': patient_info.get('blood_type', '') or 'N/A',
                'emergency_contact': patient_info.get('emergency_contact', {})
            }
            
            # Format data for OpenAI GPT-4
            formatted_data = self._format_comprehensive_data_for_gpt4(
                patient_info_enhanced, 
                statistics, 
                risk_assessment, 
                days
            )
            
            # Get AI summary (RAG-enhanced if available, otherwise basic)
            print(f"🤖 Generating AI medical analysis...")
            if self.rag_service:
                print("🧠 Using RAG-enhanced AI analysis...")
                ai_summary = self._get_rag_enhanced_summary(patient_info_enhanced, filtered_health_data, statistics, risk_assessment)
            else:
                print("🤖 Using basic GPT-4 analysis...")
                ai_summary = self._get_gpt4_summary(formatted_data)
            
            if ai_summary:
                # Prepare date range info
                date_range_info = {
                    'type': date_range_type,
                    'days': days
                }
                if date_range_type == 'custom' and start_date and end_date:
                    date_range_info['start_date'] = start_date.strftime('%Y-%m-%d')
                    date_range_info['end_date'] = end_date.strftime('%Y-%m-%d')
                
                # Return comprehensive response with all data
                comprehensive_response = {
                    'success': True,
                    'message': 'Comprehensive AI summary with risk assessment generated successfully',
                    'data': {
                        'patient_id': patient_id,
                        'patient_info': patient_info_enhanced,
                        'date_range': date_range_info,
                        'date_range_days': days,  # Keep for backward compatibility
                        'generated_at': datetime.utcnow().isoformat(),
                        'pregnancy_risk_assessment': risk_assessment,
                        'ai_summary': ai_summary,
                        'statistics': statistics,
                        'raw_data': {
                            'food_data': filtered_health_data['food_data'][:50],
                            'medications': {
                                'medication_logs': filtered_health_data['medication_history'][:50],
                                'prescriptions': filtered_health_data['prescription_documents']
                            },
                            'symptoms': filtered_health_data['symptom_analysis_reports'][:50],
                            'sleep': filtered_health_data['sleep_logs'][:50],
                            'mental_health': filtered_health_data['mental_health_logs'][:50],
                            'kick_counts': filtered_health_data['kick_count_logs'][:50],
                            'hydration': {
                                'records': filtered_health_data['hydration_records'][:50],
                                'goal': filtered_health_data['hydration_goal']
                            }
                        }
                    }
                }
                
                print(f"✅ Comprehensive AI summary generated successfully!")
                return jsonify(comprehensive_response), 200
            else:
                # Fallback to basic summary if GPT-4 fails
                print('⚠️ GPT-4 failed, using fallback summary')
                fallback_summary = self._get_fallback_summary(patient_data)
                
                # Prepare date range info
                date_range_info = {
                    'type': date_range_type,
                    'days': days
                }
                if date_range_type == 'custom' and start_date and end_date:
                    date_range_info['start_date'] = start_date.strftime('%Y-%m-%d')
                    date_range_info['end_date'] = end_date.strftime('%Y-%m-%d')
            
            return jsonify({
                'success': True,
                    'message': 'AI summary generated with fallback (GPT-4 unavailable)',
                    'data': {
                        'patient_id': patient_id,
                        'patient_info': patient_info_enhanced,
                        'date_range': date_range_info,
                        'date_range_days': days,  # Keep for backward compatibility
                        'generated_at': datetime.utcnow().isoformat(),
                        'pregnancy_risk_assessment': risk_assessment,
                        'ai_summary': fallback_summary,
                        'statistics': statistics,
                        'raw_data': {
                            'food_data': filtered_health_data['food_data'][:50],
                            'medications': {
                                'medication_logs': filtered_health_data['medication_history'][:50],
                                'prescriptions': filtered_health_data['prescription_documents']
                            },
                            'symptoms': filtered_health_data['symptom_analysis_reports'][:50],
                            'sleep': filtered_health_data['sleep_logs'][:50],
                            'mental_health': filtered_health_data['mental_health_logs'][:50],
                            'kick_counts': filtered_health_data['kick_count_logs'][:50],
                            'hydration': {
                                'records': filtered_health_data['hydration_records'][:50],
                                'goal': filtered_health_data['hydration_goal']
                            }
                        }
                    },
                    'note': 'OpenAI GPT-4 temporarily unavailable, using fallback summary'
            }), 200
            
        except Exception as e:
            print(f"❌ Error getting comprehensive AI summary: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def _format_comprehensive_data_for_gpt4(self, patient_info, statistics, risk_assessment, days):
        """Format comprehensive patient data for GPT-4 analysis"""
        formatted_data = f"""
**Patient Information:**
- Name: {patient_info['fullname']}
- Age: {patient_info['age']} years
- Pregnancy Week: {patient_info['pregnancy_week']} (Trimester {patient_info['trimester']})
- Expected Delivery: {patient_info['expected_delivery_date']}
- Date Range Analyzed: Last {days} days

**Pregnancy Risk Assessment:**
- Risk Level: {risk_assessment['overall_risk_level']} ({risk_assessment['risk_score']}/100)
- Risk Factors: {len(risk_assessment['risk_factors'])} identified
- Red Flags: {len(risk_assessment['red_flags'])}

**Statistics Summary:**
- Food/Nutrition Entries: {statistics['food_nutrition']['entries_in_range']} entries ({statistics['food_nutrition']['coverage_percentage']:.1f}% coverage)
- Medication Adherence: {statistics['medication_adherence']['adherence_rate']:.1f}%
- Symptom Reports: {statistics['symptoms_tracking']['reports_in_range']} (Severe: {statistics['symptoms_tracking']['severity_breakdown']['severe']})
- Kick Count Sessions: {statistics['kick_count_tracking']['sessions_in_range']}
- Mental Health Check-ins: {statistics['mental_health']['checkins_in_range']} (Avg mood: {statistics['mental_health']['average_mood_score']:.1f}/10)

**Detailed Risk Factors:**
{json.dumps(risk_assessment['risk_factors'], indent=2)}

**Protective Factors:**
{json.dumps(risk_assessment['protective_factors'], indent=2)}

Please provide a comprehensive medical summary analyzing this patient's pregnancy health status, highlighting key concerns and recommendations.
"""
        return formatted_data
    
    def _get_gpt4_summary(self, patient_data_text):
        """Get GPT-4 summarization of patient data"""
        try:
            import os
            from openai import OpenAI
            
            # Get OpenAI API key
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                print('❌ OpenAI API key not found')
                return None
            
            if not api_key.startswith('sk-'):
                print('❌ Invalid OpenAI API key format')
                return None
            
            print(f'✅ OpenAI API key found: {api_key[:10]}...{api_key[-4:]}')
            
            # Initialize OpenAI client
            try:
                import openai
                openai.api_key = api_key
                print('✅ OpenAI client initialized')
            except Exception as client_error:
                print(f'❌ Failed to initialize OpenAI client: {client_error}')
                return None
            
            print('🤖 Sending data to GPT-4 for analysis...')
            
            # Create comprehensive system prompt for obstetrics
            system_prompt = """You are an expert medical AI assistant specializing in obstetrics and prenatal care. 
Analyze the comprehensive patient health data provided and generate a detailed medical summary that includes:
1. Overall pregnancy health assessment
2. Analysis of nutrition, medication adherence, symptoms, fetal activity, and mental health
3. Identification of any concerning patterns or trends
4. Specific, actionable medical recommendations
5. Risk factors and protective factors
Be professional, thorough, and provide evidence-based insights."""
            
            # Call OpenAI GPT-4 API
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": patient_data_text}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
                
                ai_summary = response.choices[0].message.content
                print(f'✅ GPT-4 summary generated successfully ({len(ai_summary)} characters)')
                return ai_summary
                
            except Exception as api_error:
                error_str = str(api_error).lower()
                print(f'❌ OpenAI API call failed: {api_error}')
                
                if "invalid_api_key" in error_str or "authentication" in error_str:
                    print('💡 Invalid API key - verify your OpenAI API key')
                elif "rate_limit" in error_str:
                    print('💡 Rate limit exceeded - try again later')
                elif "model" in error_str or "gpt-4" in error_str:
                    print('💡 GPT-4 not available - falling back to gpt-3.5-turbo')
                    # Try with GPT-3.5-turbo as fallback
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": patient_data_text}
                        ],
                        max_tokens=1500,
                        temperature=0.3
                    )
                    ai_summary = response.choices[0].message.content
                    print(f'✅ GPT-3.5-turbo summary generated as fallback')
                    return ai_summary
                
                return None
            
        except Exception as e:
            print(f"❌ Error in _get_gpt4_summary: {e}")
            return None

    def _get_rag_enhanced_summary(self, patient_info, health_data, statistics, risk_assessment):
        """Get RAG-enhanced AI summary using medical knowledge base"""
        try:
            if not self.rag_service:
                print("⚠️ RAG service not available, falling back to basic GPT-4")
                return self._get_gpt4_summary(self._format_comprehensive_data_for_gpt4(
                    patient_info, statistics, risk_assessment, 30
                ))
            
            print("🧠 Retrieving medical context for RAG enhancement...")
            
            # Prepare patient data for RAG
            patient_data_for_rag = {
                'pregnancy_week': patient_info.get('pregnancy_week', 0),
                'age': patient_info.get('age', 0),
                'blood_type': patient_info.get('blood_type', ''),
                'trimester': patient_info.get('trimester', 0),
                'symptom_analysis_reports': health_data.get('symptom_analysis_reports', []),
                'medication_logs': health_data.get('medication_history', []),
                'mental_health_logs': health_data.get('mental_health_logs', []),
                'kick_count_logs': health_data.get('kick_count_logs', []),
                'sleep_logs': health_data.get('sleep_logs', []),
                'food_data': health_data.get('food_data', [])
            }
            
            # Determine query type based on patient data
            query_type = "pregnancy"  # Default
            if patient_data_for_rag['symptom_analysis_reports']:
                query_type = "symptoms"
            elif patient_data_for_rag['medication_logs']:
                query_type = "medications"
            
            # Get medical context
            medical_context = self.rag_service.get_medical_context(patient_data_for_rag, query_type)
            print(f"📚 Retrieved {len(medical_context)} medical context chunks")
            
            # Generate enhanced summary
            enhanced_summary = self.rag_service.generate_enhanced_summary(
                patient_data_for_rag, 
                medical_context, 
                query_type
            )
            
            if enhanced_summary.get('rag_enhanced', False):
                print("✅ RAG-enhanced summary generated successfully")
                return enhanced_summary['ai_summary']
            else:
                print("⚠️ RAG enhancement failed, using fallback")
                return self._get_gpt4_summary(self._format_comprehensive_data_for_gpt4(
                    patient_info, statistics, risk_assessment, 30
                ))
                
        except Exception as e:
            print(f"❌ Error in RAG-enhanced summary: {e}")
            print("🔄 Falling back to basic GPT-4 summary")
            return self._get_gpt4_summary(self._format_comprehensive_data_for_gpt4(
                patient_info, statistics, risk_assessment, 30
            ))

    def _format_patient_data_for_openai(self, patient_data):
        """Format patient data for OpenAI analysis"""
        patient_info = patient_data.get('patient_info', {})
        health_data = patient_data.get('health_data', {})
        summary = patient_data.get('summary', {})
        
        formatted_data = f"""
PATIENT SUMMARY REPORT
=====================

PATIENT INFORMATION:
- Name: {patient_info.get('full_name', 'Unknown')}
- Email: {patient_info.get('email', 'N/A')}
- Age: {patient_info.get('age', 'N/A')}
- Blood Type: {patient_info.get('blood_type', 'N/A')}
- Gender: {patient_info.get('gender', 'N/A')}
- Pregnant: {patient_info.get('is_pregnant', False)}
- Status: {patient_info.get('status', 'N/A')}
- Date of Birth: {patient_info.get('date_of_birth', 'N/A')}
- Mobile: {patient_info.get('mobile', 'N/A')}
- Address: {patient_info.get('address', 'N/A')}
- Emergency Contact: {patient_info.get('emergency_contact', {})}

HEALTH DATA SUMMARY:
- Total Appointments: {summary.get('total_appointments', 0)}
- Food & Nutrition Entries: {summary.get('total_food_entries', 0)}
- Symptom Analysis Reports: {summary.get('total_symptoms', 0)}
- Mental Health Logs: {summary.get('total_mental_health', 0)}
- Medication History: {summary.get('total_medications', 0)}
- Kick Count Logs: {summary.get('total_kick_logs', 0)}
- Prescription Documents: {summary.get('total_prescriptions', 0)}
- Vital Signs Logs: {summary.get('total_vital_signs', 0)}

DETAILED HEALTH INFORMATION:
"""

        # Add detailed health data
        if health_data.get('food_data'):
            formatted_data += "\nFOOD & NUTRITION LOGS:\n"
            for i, food in enumerate(health_data['food_data'][:5]):  # Limit to 5 entries
                formatted_data += f"- {food.get('food_input', 'N/A')} ({food.get('meal_type', 'N/A')})\n"
        
        if health_data.get('symptom_analysis_reports'):
            formatted_data += "\nSYMPTOM ANALYSIS REPORTS:\n"
            for i, symptom in enumerate(health_data['symptom_analysis_reports'][:5]):  # Limit to 5 entries
                formatted_data += f"- {symptom.get('symptom_text', 'N/A')} (Severity: {symptom.get('severity', 'N/A')})\n"
        
        if health_data.get('mental_health_logs'):
            formatted_data += "\nMENTAL HEALTH LOGS:\n"
            for i, mood in enumerate(health_data['mental_health_logs'][:5]):  # Limit to 5 entries
                formatted_data += f"- Mood: {mood.get('mood', 'N/A')} (Date: {mood.get('date', 'N/A')})\n"
        
        if health_data.get('appointments'):
            formatted_data += "\nAPPOINTMENTS:\n"
            for i, appointment in enumerate(health_data['appointments'][:5]):  # Limit to 5 entries
                formatted_data += f"- {appointment.get('appointment_type', 'N/A')} on {appointment.get('appointment_date', 'N/A')} at {appointment.get('appointment_time', 'N/A')}\n"
        
        return formatted_data

    def _get_openai_summary(self, patient_data_text):
        """Get OpenAI summarization of patient data"""
        try:
            import os
            from openai import OpenAI
            
            # Get OpenAI API key from environment variables
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                print('❌ OpenAI API key not found in environment variables')
                print('💡 For local development: Add OPENAI_API_KEY to .env file')
                print('💡 For Render deployment: Set OPENAI_API_KEY in Render Dashboard > Environment')
                return None
            
            if not api_key.startswith('sk-'):
                print('❌ Invalid OpenAI API key format (should start with sk-)')
                print(f'   Current key format: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}')
                return None
            
            print(f'✅ OpenAI API key found: {api_key[:10]}...{api_key[-4:]}')
            
            # Simple OpenAI client initialization for version 1.3.0
            try:
                import openai
                openai.api_key = api_key
                print('✅ OpenAI client initialized with simple method')
            except Exception as client_error:
                print(f'❌ Failed to initialize OpenAI client: {client_error}')
                print(f'   Error type: {type(client_error).__name__}')
                return None
            
            print('🤖 Sending data to OpenAI for summarization...')
            
            # Create the prompt for OpenAI
            prompt = f"""
Please analyze the following patient data and provide a comprehensive medical summary. Focus on:

1. Patient Overview (demographics, pregnancy status, general health indicators)
2. Health Data Analysis (patterns in symptoms, nutrition, mental health)
3. Key Concerns or Recommendations
4. Overall Health Assessment
5. Priority Areas for Medical Attention

Patient Data:
{patient_data_text}

Please provide a clear, professional medical summary suitable for a doctor's review.
"""
            
            # Call OpenAI API with simple method
            try:
                print('📡 Making OpenAI API request...')
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                    {"role": "system", "content": "You are a medical AI assistant that analyzes patient data and provides professional medical summaries for doctors."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
                print('✅ OpenAI API call successful')
            
                print(f'✅ OpenAI API response received: {response.usage.total_tokens} tokens used')
                print(f'✅ Model used: {response.model}')
                return response.choices[0].message.content
            
            except Exception as openai_error:
                print(f'❌ OpenAI API call failed: {openai_error}')
                print(f'   Error type: {type(openai_error).__name__}')
                print(f'   Error details: {str(openai_error)}')
                
                # Handle specific OpenAI errors
                error_str = str(openai_error).lower()
                if "insufficient_quota" in error_str:
                    print('💡 OpenAI API quota exceeded - check your billing')
                elif "invalid_api_key" in error_str or "authentication" in error_str:
                    print('💡 Invalid API key - verify your OpenAI API key')
                elif "rate_limit" in error_str:
                    print('💡 Rate limit exceeded - try again later')
                elif "timeout" in error_str:
                    print('💡 Request timeout - OpenAI API may be slow')
                elif "connection" in error_str:
                    print('💡 Connection error - check network connectivity')
                else:
                    print(f'💡 Unknown OpenAI error: {error_str}')
                
                return None
            
        except ImportError as import_error:
            print(f'❌ OpenAI library not installed: {import_error}')
            print('💡 Install with: pip install openai')
            return None
        except Exception as e:
            print(f'❌ Unexpected error with OpenAI API: {e}')
            print(f'   Error type: {type(e).__name__}')
            print(f'   Error details: {str(e)}')
            return None
    
    def _get_fallback_summary(self, patient_data):
        """Generate a simple summary without AI"""
        try:
            patient_info = patient_data.get('patient_info', {})
            summary_stats = patient_data.get('summary', {})
            
            # Extract key information
            name = patient_info.get('full_name', 'Unknown Patient')
            age = patient_info.get('age', 'N/A')
            gender = patient_info.get('gender', 'N/A')
            blood_type = patient_info.get('blood_type', 'N/A')
            is_pregnant = patient_info.get('is_pregnant', False)
            
            # Count health data
            total_medications = summary_stats.get('total_medications', 0)
            total_symptoms = summary_stats.get('total_symptoms', 0)
            total_food_entries = summary_stats.get('total_food_entries', 0)
            total_mental_health = summary_stats.get('total_mental_health', 0)
            total_appointments = summary_stats.get('total_appointments', 0)
            
            # Generate summary
            summary = f"""PATIENT HEALTH SUMMARY (Fallback Mode)
=====================================

PATIENT OVERVIEW:
- Name: {name}
- Age: {age}
- Gender: {gender}
- Blood Type: {blood_type}
- Pregnancy Status: {'Pregnant' if is_pregnant else 'Not Pregnant'}

HEALTH DATA SUMMARY:
- Total Medications: {total_medications}
- Symptom Reports: {total_symptoms}
- Food/Nutrition Entries: {total_food_entries}
- Mental Health Logs: {total_mental_health}
- Appointments: {total_appointments}

HEALTH ASSESSMENT:
Based on the available data, this patient has {'active' if (total_medications + total_symptoms + total_food_entries + total_mental_health) > 0 else 'limited'} health monitoring activity.

RECOMMENDATIONS:
1. Continue regular health monitoring through the platform
2. {'Maintain medication compliance' if total_medications > 0 else 'Consider medication management if needed'}
3. {'Monitor symptom patterns' if total_symptoms > 0 else 'Track symptoms for early detection'}
4. {'Continue nutrition tracking' if total_food_entries > 0 else 'Consider adding nutrition logging'}
5. {'Maintain mental health awareness' if total_mental_health > 0 else 'Consider mental health monitoring'}

PRIORITY AREAS:
- Regular medical check-ups
- Medication adherence {'(active monitoring needed)' if total_medications > 0 else '(no current medications)'}
- Symptom tracking {'(ongoing)' if total_symptoms > 0 else '(no recent symptoms)'}
- Overall health maintenance

NOTE: This is a fallback summary generated without AI assistance. 
For more detailed analysis, the OpenAI integration needs to be restored."""
            
            return summary.strip()
            
        except Exception as e:
            print(f'❌ Error generating fallback summary: {e}')
            return "Error generating summary. Please try again later."
    
    def get_appointments(self, request) -> tuple:
        """Get appointments for doctor"""
        try:
            # For doctor-only app, we don't need to validate doctor_id
            # Get appointments from the database using the working logic from app_simple.py
            if hasattr(self.doctor_model, 'db') and hasattr(self.doctor_model.db, 'patients_collection'):
                patients_collection = self.doctor_model.db.patients_collection
                
                # Get query parameters for filtering
                patient_id = request.args.get('patient_id')
                date = request.args.get('date')
                status = request.args.get('status', 'active')
                
                print(f"🔍 Getting appointments - patient_id: {patient_id}, date: {date}, status: {status}")
                
                all_appointments = []
                
                if patient_id:
                    # Get appointments for specific patient
                    patient = patients_collection.find_one({"patient_id": patient_id})
                    if patient and 'appointments' in patient:
                        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                        for appointment in patient['appointments']:
                            appointment_data = appointment.copy()
                            appointment_data['patient_id'] = patient_id
                            appointment_data['patient_name'] = patient_name
                            
                            # Filter by date if provided
                            if not date or appointment.get('appointment_date') == date:
                                all_appointments.append(appointment_data)
                else:
                    # Get appointments from all patients that have appointments
                    patients = patients_collection.find({"appointments": {"$exists": True, "$ne": []}})
                    
                    for patient in patients:
                        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                        
                        for appointment in patient.get('appointments', []):
                            appointment_data = appointment.copy()
                            appointment_data['patient_id'] = patient['patient_id']
                            appointment_data['patient_name'] = patient_name
                            
                            # Filter by date if provided
                            if not date or appointment.get('appointment_date') == date:
                                all_appointments.append(appointment_data)
                
                # Sort by appointment date
                all_appointments.sort(key=lambda x: x.get('appointment_date', ''))
                
                print(f"✅ Found {len(all_appointments)} appointments")
                
                return jsonify({
                    "appointments": all_appointments,
                    "total_count": len(all_appointments),
                    "message": "Appointments retrieved successfully"
                }), 200
            else:
                return jsonify({'error': 'Database connection not available'}), 500
            
        except Exception as e:
            print(f"❌ Error retrieving appointments: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def create_appointment(self, request) -> tuple:
        """Create a new appointment - saved in patient document"""
        try:
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            data = request.get_json()
            print(f"🔍 Creating appointment - data: {data}")
            
            # Validate required fields
            required_fields = ['patient_id', 'appointment_date', 'appointment_time']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Check if patient exists
            patient = patients_collection.find_one({"patient_id": data["patient_id"]})
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            print(f"✅ Patient found: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            
            # Generate unique appointment ID
            from bson import ObjectId
            appointment_id = str(ObjectId())
            
            # Create appointment object
            appointment = {
                "appointment_id": appointment_id,
                "appointment_date": data["appointment_date"],
                "appointment_time": data["appointment_time"],
                "appointment_type": data.get("appointment_type", "General"),
                "appointment_status": "scheduled",
                "notes": data.get("notes", ""),
                "doctor_id": data.get("doctor_id", ""),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                # Reminder tracking fields
                "reminder_sent": False,
                "reminder_sent_at": None
            }
            
            print(f"💾 Saving appointment to patient {data['patient_id']}: {appointment}")
            
            # Add appointment to patient's appointments array
            result = patients_collection.update_one(
                {"patient_id": data["patient_id"]},
                {"$push": {"appointments": appointment}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Appointment saved successfully!")
                return jsonify({
                    "appointment_id": appointment_id,
                    "message": "Appointment created successfully"
                }), 201
            else:
                return jsonify({'error': 'Failed to save appointment'}), 500
            
        except Exception as e:
            print(f"❌ Error creating appointment: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_appointment_by_id(self, request, appointment_id: str) -> tuple:
        """Get a single appointment by ID"""
        try:
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            print(f"🔍 Getting appointment {appointment_id}")
            
            # Find the patient with this appointment
            patient = patients_collection.find_one({
                "appointments.appointment_id": appointment_id
            })
            
            if not patient:
                return jsonify({'error': 'Appointment not found'}), 404
            
            # Find the specific appointment in the appointments array
            appointment = None
            for apt in patient.get('appointments', []):
                if apt.get('appointment_id') == appointment_id:
                    appointment = apt
                    # Add patient name to the appointment
                    patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                    appointment['patient_name'] = patient_name
                    appointment['patient_id'] = patient.get('patient_id')
                    break
            
            if not appointment:
                return jsonify({'error': 'Appointment not found'}), 404
            
            print(f"✅ Found appointment: {appointment.get('appointment_date')} at {appointment.get('appointment_time')}")
            
            return jsonify({
                'success': True,
                'appointment': appointment
            }), 200
            
        except Exception as e:
            print(f"❌ Error getting appointment: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def update_appointment(self, request, appointment_id: str) -> tuple:
        """Update an appointment"""
        try:
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            data = request.get_json()
            
            print(f"🔍 Updating appointment {appointment_id} with data: {data}")
            
            # Find the patient with this appointment
            patient = patients_collection.find_one({
                "appointments.appointment_id": appointment_id
            })
            
            if not patient:
                return jsonify({'error': 'Appointment not found'}), 404
            
            # Build update fields
            update_fields = {}
            if 'appointment_date' in data:
                update_fields['appointments.$.appointment_date'] = data['appointment_date']
            if 'appointment_time' in data:
                update_fields['appointments.$.appointment_time'] = data['appointment_time']
            if 'appointment_type' in data:
                update_fields['appointments.$.appointment_type'] = data['appointment_type']
            if 'appointment_mode' in data:
                update_fields['appointments.$.appointment_mode'] = data['appointment_mode']
            if 'video_link' in data:
                update_fields['appointments.$.video_link'] = data['video_link']
            if 'appointment_status' in data:
                update_fields['appointments.$.appointment_status'] = data['appointment_status']
            if 'notes' in data:
                update_fields['appointments.$.notes'] = data['notes']
            
            update_fields['appointments.$.updated_at'] = datetime.now().isoformat()
            
            # Update the appointment
            result = patients_collection.update_one(
                {"appointments.appointment_id": appointment_id},
                {"$set": update_fields}
            )
            
            if result.modified_count > 0:
                print(f"✅ Appointment {appointment_id} updated successfully")
                return jsonify({
                    'success': True,
                    'message': 'Appointment updated successfully',
                    'appointment_id': appointment_id
                }), 200
            else:
                return jsonify({'error': 'No changes made or appointment not found'}), 400
            
        except Exception as e:
            print(f"❌ Error updating appointment: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def delete_appointment(self, request, appointment_id: str) -> tuple:
        """Delete an appointment"""
        try:
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            print(f"🔍 Deleting appointment {appointment_id}")
            
            # Find the patient with this appointment
            patient = patients_collection.find_one({
                "appointments.appointment_id": appointment_id
            })
            
            if not patient:
                return jsonify({'error': 'Appointment not found'}), 404
            
            # Remove the appointment from the array
            result = patients_collection.update_one(
                {"appointments.appointment_id": appointment_id},
                {"$pull": {"appointments": {"appointment_id": appointment_id}}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Appointment {appointment_id} deleted successfully")
                return jsonify({
                    'success': True,
                    'message': 'Appointment deleted successfully',
                    'appointment_id': appointment_id
                }), 200
            else:
                return jsonify({'error': 'Failed to delete appointment'}), 500
            
        except Exception as e:
            print(f"❌ Error deleting appointment: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_dashboard_stats(self, request) -> tuple:
        """Get dashboard statistics for doctor"""
        try:
            # For doctor-only app, we don't need to validate doctor_id
            # Get real statistics from the database
            if hasattr(self.doctor_model, 'db') and hasattr(self.doctor_model.db, 'patients_collection'):
                patients_collection = self.doctor_model.db.patients_collection
                
                # Get real patient count
                total_patients = patients_collection.count_documents({"status": {"$ne": "deleted"}})
                
                # Get appointments count
                patients_with_appointments = patients_collection.find({"appointments": {"$exists": True, "$ne": []}})
                total_appointments = 0
                for patient in patients_with_appointments:
                    total_appointments += len(patient.get('appointments', []))
                
                # Sample dashboard statistics (you can enhance this with real data)
                stats = {
                    'total_patients': total_patients,
                    'total_appointments': total_appointments,
                    'today_appointments': 0,  # You can implement date filtering
                    'pending_appointments': 0,  # You can implement status filtering
                    'completed_appointments': 0,  # You can implement status filtering
                    'revenue_today': 0.00,
                    'revenue_month': 0.00
                }
                
                return jsonify({
                    'success': True,
                    'stats': stats
                }), 200
            else:
                return jsonify({'error': 'Database connection not available'}), 500
            
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def get_medication_history(self, request, patient_id: str) -> tuple:
        """Get medication history for a patient"""
        try:
            print(f"🔍 Getting medication history for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get medication logs from patient document
            medication_logs = patient.get('medication_logs', [])
            
            # Convert ObjectId to string for JSON serialization
            for log in medication_logs:
                if '_id' in log:
                    log['_id'] = str(log['_id'])
            
            # Sort by newest first (using created_at or timestamp)
            medication_logs.sort(key=lambda x: x.get('created_at', x.get('timestamp', '')), reverse=True)
            
            print(f"✅ Retrieved {len(medication_logs)} medication logs for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'medication_logs': medication_logs,
                'totalEntries': len(medication_logs)
            }), 200
            
        except Exception as e:
            print(f"Error getting medication history: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_symptom_analysis_reports(self, request, patient_id: str) -> tuple:
        """Get only the AI analysis reports for a patient"""
        try:
            print(f"🔍 Getting analysis reports for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get analysis reports from patient document
            analysis_reports = patient.get('symptom_analysis_reports', [])
            
            # Sort by timestamp (newest first)
            analysis_reports.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')), reverse=True)
            
            print(f"✅ Retrieved {len(analysis_reports)} analysis reports for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'analysis_reports': analysis_reports,
                'totalReports': len(analysis_reports)
            }), 200
            
        except Exception as e:
            print(f"Error getting analysis reports: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_food_entries(self, request, patient_id: str) -> tuple:
        """Get food entries from patient's food_data array"""
        try:
            print(f"🍽️ Getting food entries for user ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({
                    'success': False,
                    'message': f'Patient not found with ID: {patient_id}'
                }), 404
            
            # Get food_data array from patient document
            food_data = patient.get('food_data', [])
            
            # Sort by timestamp (most recent first)
            food_data.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')), reverse=True)
            
            print(f"✅ Retrieved {len(food_data)} food entries for user: {patient_id}")
            
            return jsonify({
                'success': True,
                'user_id': patient_id,
                'food_data': food_data,
                'total_entries': len(food_data)
            }), 200
            
        except Exception as e:
            print(f"❌ Error getting food entries: {e}")
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
    def get_tablet_tracking_history(self, request, patient_id: str) -> tuple:
        """Get tablet tracking history for a patient"""
        try:
            print(f"🔍 Getting tablet tracking history for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get tablet tracking logs from patient document
            tablet_logs = patient.get('tablet_tracking_logs', [])
            
            # Sort by newest first
            tablet_logs.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')), reverse=True)
            
            print(f"✅ Retrieved {len(tablet_logs)} tablet tracking logs for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'tablet_logs': tablet_logs,
                'totalEntries': len(tablet_logs)
            }), 200
            
        except Exception as e:
            print(f"Error getting tablet tracking history: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_patient_profile(self, request, patient_id: str) -> tuple:
        """Get patient profile information"""
        try:
            print(f"🔍 Getting patient profile for ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Format patient profile
            profile = {
                'patient_id': patient.get('patient_id', ''),
                'username': patient.get('username', ''),
                'email': patient.get('email', ''),
                'first_name': patient.get('first_name', ''),
                'last_name': patient.get('last_name', ''),
                'full_name': f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown'),
                'date_of_birth': patient.get('date_of_birth', ''),
                'blood_type': patient.get('blood_type', ''),
                'mobile': patient.get('mobile', ''),
                'address': patient.get('address', ''),
                'is_pregnant': patient.get('is_pregnant', False),
                'pregnancy_due_date': patient.get('pregnancy_due_date', ''),
                'is_profile_complete': patient.get('is_profile_complete', False),
                'status': patient.get('status', 'active'),
                'created_at': patient.get('created_at', ''),
                'last_login': patient.get('last_login', ''),
                'object_id': str(patient.get('_id', ''))
            }
            
            print(f"✅ Retrieved profile for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'profile': profile
            }), 200
            
        except Exception as e:
            print(f"Error getting patient profile: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_kick_count_history(self, request, patient_id: str) -> tuple:
        """Get kick count history for a patient"""
        try:
            print(f"🔍 Getting kick count history for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get kick count logs from patient document
            kick_logs = patient.get('kick_count_logs', [])
            
            # Sort by newest first
            kick_logs.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')), reverse=True)
            
            print(f"✅ Retrieved {len(kick_logs)} kick count logs for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'kick_logs': kick_logs,
                'totalEntries': len(kick_logs)
            }), 200
            
        except Exception as e:
            print(f"Error getting kick count history: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_mental_health_history(self, request, patient_id: str) -> tuple:
        """Get mental health history for a patient"""
        try:
            print(f"🔍 Getting mental health history for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get mental health logs from patient document
            mental_health_logs = patient.get('mental_health_logs', [])
            
            # Convert ObjectId to string for JSON serialization
            for log in mental_health_logs:
                if '_id' in log:
                    log['_id'] = str(log['_id'])
            
            # Sort by newest first
            mental_health_logs.sort(key=lambda x: x.get('date', x.get('created_at', '')), reverse=True)
            
            print(f"✅ Retrieved {len(mental_health_logs)} mental health logs for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'data': {
                    'patient_id': patient_id,
                    'mood_history': mental_health_logs,
                    'assessment_history': [],
                    'total_mood_entries': len(mental_health_logs),
                    'total_assessment_entries': 0
                }
            }), 200
            
        except Exception as e:
            print(f"❌ Get mental health history error: {e}")
            return jsonify({
                'success': False,
                'message': f'Internal server error: {str(e)}'
            }), 500
    
    def get_prescription_documents(self, request, patient_id: str) -> tuple:
        """Get prescription documents for a patient"""
        try:
            print(f"🔍 Getting prescription documents for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get prescription documents from patient document
            prescription_documents = patient.get('prescription_documents', [])
            
            # Sort by newest first
            prescription_documents.sort(key=lambda x: x.get('created_at', x.get('date', '')), reverse=True)
            
            print(f"✅ Retrieved {len(prescription_documents)} prescription documents for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'prescription_documents': prescription_documents,
                'totalDocuments': len(prescription_documents)
            }), 200
            
        except Exception as e:
            print(f"Error getting prescription documents: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_vital_signs_history(self, request, patient_id: str) -> tuple:
        """Get vital signs history for a patient"""
        try:
            print(f"🔍 Getting vital signs history for patient ID: {patient_id}")
            
            if not hasattr(self.doctor_model, 'db') or not hasattr(self.doctor_model.db, 'patients_collection'):
                return jsonify({'error': 'Database connection not available'}), 500
            
            patients_collection = self.doctor_model.db.patients_collection
            
            # Find patient by Patient ID
            patient = patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            # Get vital signs logs from patient document
            vital_signs_logs = patient.get('vital_signs_logs', [])
            
            # Sort by newest first
            vital_signs_logs.sort(key=lambda x: x.get('created_at', x.get('date', '')), reverse=True)
            
            print(f"✅ Retrieved {len(vital_signs_logs)} vital signs logs for patient: {patient_id}")
            
            return jsonify({
                'success': True,
                'patientId': patient_id,
                'vital_signs_logs': vital_signs_logs,
                'totalEntries': len(vital_signs_logs)
            }), 200
            
        except Exception as e:
            print(f"Error getting vital signs history: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    def get_profile_fields(self, request) -> tuple:
        """Get doctor profile fields - returns available fields for profile completion"""
        try:
            # Return the list of fields that can be updated in doctor profile
            profile_fields = {
                'personal_info': {
                    'first_name': {'type': 'string', 'required': True, 'description': 'Doctor first name'},
                    'last_name': {'type': 'string', 'required': True, 'description': 'Doctor last name'},
                    'email': {'type': 'email', 'required': True, 'description': 'Doctor email address'},
                    'mobile': {'type': 'string', 'required': True, 'description': 'Doctor mobile number'}
                },
                'professional_info': {
                    'specialization': {'type': 'string', 'required': True, 'description': 'Medical specialization'},
                    'license_number': {'type': 'string', 'required': True, 'description': 'Medical license number'},
                    'experience_years': {'type': 'number', 'required': True, 'description': 'Years of experience'},
                    'qualifications': {'type': 'array', 'required': False, 'description': 'List of qualifications'}
                },
                'practice_info': {
                    'hospital_name': {'type': 'string', 'required': False, 'description': 'Hospital or clinic name'},
                    'consultation_fee': {'type': 'number', 'required': False, 'description': 'Consultation fee'},
                    'available_timings': {'type': 'object', 'required': False, 'description': 'Available consultation timings'},
                    'languages': {'type': 'array', 'required': False, 'description': 'Languages spoken'}
                },
                'address_info': {
                    'address': {'type': 'string', 'required': False, 'description': 'Practice address'},
                    'city': {'type': 'string', 'required': False, 'description': 'City'},
                    'state': {'type': 'string', 'required': False, 'description': 'State'},
                    'pincode': {'type': 'string', 'required': False, 'description': 'Pincode'}
                }
            }
            
            return jsonify({
                'success': True,
                'profile_fields': profile_fields,
                'message': 'Available doctor profile fields'
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500

    def cancel_connection_request(self, request) -> tuple:
        """Doctor cancels pending connection request"""
        try:
            data = request.get_json()
            doctor_id = request.user_data.get('doctor_id')
            
            if not doctor_id:
                return jsonify({"success": False, "error": "Doctor authentication required"}), 403
            
            # Validate required fields
            if not data.get('connection_id'):
                return jsonify({"success": False, "error": "connection_id is required"}), 400
            
            connection_id = data['connection_id']
            reason = data.get('reason', '')
            
            # Import database instance
            from models.database import Database
            db = Database()
            
            # Get connection
            connection = db.connections_collection.find_one({"connection_id": connection_id})
            
            if not connection:
                return jsonify({"success": False, "error": "Connection request not found"}), 404
            
            # Verify doctor owns this connection
            if connection['doctor_id'] != doctor_id:
                return jsonify({"success": False, "error": "Not your connection request"}), 403
            
            # Check if request is pending
            if connection['status'] != 'pending':
                return jsonify({
                    "success": False, 
                    "error": f"Cannot cancel request with status: {connection['status']}"
                }), 400
            
            # Cancel the request
            result = db.connections_collection.update_one(
                {"connection_id": connection_id, "status": "pending"},
                {
                    "$set": {
                        "status": "cancelled",
                        "dates.cancelled_at": datetime.utcnow(),
                        "dates.updated_at": datetime.utcnow(),
                        "cancellation_info": {
                            "cancelled_by": doctor_id,
                            "cancelled_by_type": "doctor",
                            "reason": reason,
                            "cancelled_at": datetime.utcnow()
                        }
                    },
                    "$push": {
                        "audit_log": {
                            "action": "request_cancelled",
                            "actor_id": doctor_id,
                            "actor_type": "doctor",
                            "timestamp": datetime.utcnow(),
                            "details": {"reason": reason}
                        }
                    }
                }
            )
            
            if result.modified_count == 0:
                return jsonify({"success": False, "error": "Failed to cancel request"}), 500
            
            print(f"✅ Doctor {doctor_id} cancelled connection request {connection_id}")
            
            return jsonify({
                "success": True,
                "message": "Connection request cancelled successfully",
                "request": {
                    "connection_id": connection_id,
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow().isoformat()
                }
            }), 200
            
        except Exception as e:
            print(f"❌ Error cancelling connection request: {e}")
            return jsonify({"success": False, "error": f"Failed to cancel request: {str(e)}"}), 500