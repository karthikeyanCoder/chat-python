"""
Sleep & Activity Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 2378-2730
Business logic for sleep tracking and user activity management

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
import json
from app.core.database import db
from app.shared.activity_tracker import activity_tracker


def save_sleep_log_service(data):
    """Save sleep log data to MongoDB - EXACT from line 2378"""
    try:
        # Debug logging
        print(f"[*] Received sleep log data: {json.dumps(data, indent=2)}")
        
        # Validate required fields
        required_fields = ['userId', 'userRole', 'startTime', 'endTime', 'totalSleep', 'sleepRating']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Check if we have Patient ID for precise linking
        patient_id = data.get('userId')
        if not patient_id:
            return jsonify({
                'success': False, 
                'message': 'Patient ID is required for precise patient linking. Please ensure you are logged in.',
                'debug_info': {
                    'received_userId': data.get('userId'),
                    'received_data': data
                }
            }), 400
        
        # Create sleep log document
        sleep_log = {
            'userId': data['userId'],
            'userRole': data['userRole'],
            'username': data.get('username', 'unknown'),
            'email': data.get('email', 'unknown'),  # Add email for better user linking
            'startTime': data['startTime'],
            'endTime': data['endTime'],
            'totalSleep': data['totalSleep'],
            'smartAlarmEnabled': data.get('smartAlarmEnabled', False),
            'optimalWakeUpTime': data.get('optimalWakeUpTime', ''),
            'sleepRating': data['sleepRating'],
            'notes': data.get('notes', ''),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'createdAt': datetime.now(),
        }
        
        # Store sleep log within the patient's document
        if data['userRole'] == 'doctor':
            # For doctors, store in separate collection (as before)
            collection = db.doctors_collection
            result = collection.insert_one(sleep_log)
            
            if result.inserted_id:
                return jsonify({
                    'success': True,
                    'message': 'Sleep log saved successfully',
                    'sleepLogId': str(result.inserted_id)
                }), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to save sleep log'}), 500
        else:
            # For patients, store within their patient document using Patient ID
            patient_id = data.get('userId')
            if not patient_id:
                return jsonify({
                    'success': False, 
                    'message': 'Patient ID is required. Please ensure you are logged in.',
                    'debug_info': {
                        'received_userId': data.get('userId'),
                        'received_data': data
                    }
                }), 400
            
            print(f"[*] Looking for patient with ID: {patient_id}")
            
            # Find patient by Patient ID (more reliable than email)
            patient = db.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
            
            print(f"[*] Found patient: {patient.get('username')} ({patient.get('email')})")
            
            # Create sleep log entry (without MongoDB _id)
            sleep_log_entry = {
                'startTime': data['startTime'],
                'endTime': data['endTime'],
                'totalSleep': data['totalSleep'],
                'smartAlarmEnabled': data.get('smartAlarmEnabled', False),
                'optimalWakeUpTime': data.get('optimalWakeUpTime', ''),
                'sleepRating': data['sleepRating'],
                'notes': data.get('notes', ''),
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'createdAt': datetime.now(),
            }
            
            # Add sleep log to patient's sleep_logs array using Patient ID
            result = db.patients_collection.update_one(
                {"patient_id": patient_id},
                {
                    "$push": {"sleep_logs": sleep_log_entry},
                    "$set": {"last_updated": datetime.now()}
                }
            )
            
            if result.modified_count > 0:
                # Log the sleep log activity
                activity_tracker.log_activity(
                    user_email=patient.get('email'),
                    activity_type="sleep_log_created",
                    activity_data={
                        "sleep_log_id": "embedded_in_patient_doc",
                        "sleep_data": sleep_log_entry,
                        "patient_id": patient_id,
                        "total_sleep_logs": len(patient.get('sleep_logs', [])) + 1
                    }
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Sleep log saved successfully to patient profile',
                    'patientId': patient_id,
                    'patientEmail': patient.get('email'),
                    'sleepLogsCount': len(patient.get('sleep_logs', [])) + 1
                }), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to save sleep log to patient profile'}), 500
            
    except Exception as e:
        print(f"Error saving sleep log: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_sleep_logs_service(username):
    """Get sleep logs for a specific user - EXACT from line 2507"""
    try:
        # Get user role from the username
        user_doc = db.patients_collection.find_one({"username": username})
        if not user_doc:
            # Try doctors collection
            user_doc = db.doctors_collection.find_one({"username": username})
            if not user_doc:
                return jsonify({'success': False, 'message': 'User not found'}), 404
        
        user_role = user_doc.get('role', 'patient')
        
        # Get sleep logs for this user
        if user_role == 'doctor':
            collection = db.doctors_collection
        else:
            collection = db.patients_collection
        
        # Find all sleep logs for this user
        sleep_logs = list(collection.find(
            {"username": username, "startTime": {"$exists": True}},
            {"_id": 0}  # Exclude MongoDB _id
        ))
        
        return jsonify({
            'success': True,
            'username': username,
            'userRole': user_role,
            'sleepLogs': sleep_logs,
            'count': len(sleep_logs)
        }), 200
        
    except Exception as e:
        print(f"Error retrieving sleep logs: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_sleep_logs_by_email_service(email):
    """Get sleep logs for a specific user by email - EXACT from line 2545"""
    try:
        # Get user role from the email
        user_doc = db.patients_collection.find_one({"email": email})
        if not user_doc:
            # Try doctors collection
            user_doc = db.doctors_collection.find_one({"email": email})
            if not user_doc:
                return jsonify({'success': False, 'message': 'User not found with this email'}), 404
        
        user_role = user_doc.get('role', 'patient')
        username = user_doc.get('username', 'unknown')
        
        # Get sleep logs for this user by email
        if user_role == 'doctor':
            # For doctors, get from separate collection
            collection = db.doctors_collection
            sleep_logs = list(collection.find(
                {"email": email, "startTime": {"$exists": True}},
                {"_id": 0}  # Exclude MongoDB _id
            ))
        else:
            # For patients, get from their document's sleep_logs array
            sleep_logs = user_doc.get('sleep_logs', [])
        
        return jsonify({
            'success': True,
            'email': email,
            'username': username,
            'userRole': user_role,
            'sleepLogs': sleep_logs,
            'count': len(sleep_logs)
        }), 200
        
    except Exception as e:
        print(f"Error retrieving sleep logs by email: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_patient_complete_profile_service(email):
    """Get complete patient profile including all health data - EXACT from line 2585"""
    try:
        # Find patient by email
        patient = db.patients_collection.find_one({"email": email})
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found with this email'}), 404
        
        # Return complete patient profile with all data
        complete_profile = {
            'success': True,
            'patient_id': patient.get('patient_id'),
            'username': patient.get('username'),
            'email': patient.get('email'),
            'mobile': patient.get('mobile'),
            'first_name': patient.get('first_name'),
            'last_name': patient.get('last_name'),
            'age': patient.get('age'),
            'blood_type': patient.get('blood_type'),
            'weight': patient.get('weight'),
            'height': patient.get('height'),
            'is_pregnant': patient.get('is_pregnant'),
            'last_period_date': patient.get('last_period_date'),
            'pregnancy_week': patient.get('pregnancy_week'),
            'expected_delivery_date': patient.get('expected_delivery_date'),
            'emergency_contact': patient.get('emergency_contact'),
            'preferences': patient.get('preferences'),
            'profile_completed_at': patient.get('profile_completed_at'),
            'last_updated': patient.get('last_updated'),
            'health_data': {
                'sleep_logs': patient.get('sleep_logs', []),
                'sleep_logs_count': len(patient.get('sleep_logs', [])),
                'food_logs': patient.get('food_logs', []),
                'food_logs_count': len(patient.get('food_logs', [])),
                'medication_logs': patient.get('medication_logs', []),
                'medication_logs_count': len(patient.get('medication_logs', [])),
                'symptom_logs': patient.get('symptom_logs', []),
                'symptom_logs_count': len(patient.get('symptom_logs', [])),
                'mental_health_logs': patient.get('mental_health_logs', []),
                'mental_health_logs_count': len(patient.get('mental_health_logs', [])),
                'kick_count_logs': patient.get('kick_count_logs', []),
                'kick_count_logs_count': len(patient.get('kick_count_logs', [])),
            }
        }
        
        return jsonify(complete_profile), 200
        
    except Exception as e:
        print(f"Error retrieving complete patient profile: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_user_activities_service(email):
    """Get all activities for a specific user - EXACT from line 2638"""
    try:
        activities = activity_tracker.get_user_activities(email)
        return jsonify({
            'success': True,
            'user_email': email,
            'activities': activities,
            'total_sessions': len(activities)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_session_activities_service(session_id):
    """Get all activities for a specific session - EXACT from line 2652"""
    try:
        session = activity_tracker.get_session_activities(session_id)
        if session:
            return jsonify({
                'success': True,
                'session': session
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_activity_summary_service(email):
    """Get summary of user activities - EXACT from line 2667"""
    try:
        summary = activity_tracker.get_activity_summary(email)
        return jsonify({
            'success': True,
            'user_email': email,
            'summary': summary,
            'total_activities': sum(item['count'] for item in summary)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def track_activity_service(data):
    """Manually track a user activity - EXACT from line 2681"""
    try:
        user_email = data.get('email')
        activity_type = data.get('activity_type')
        activity_data = data.get('activity_data', {})
        session_id = data.get('session_id')
        
        if not user_email or not activity_type:
            return jsonify({'success': False, 'message': 'Email and activity_type are required'}), 400
        
        # Log the activity
        activity_id = activity_tracker.log_activity(
            user_email=user_email,
            activity_type=activity_type,
            activity_data=activity_data,
            session_id=session_id
        )
        
        if activity_id:
            return jsonify({
                'success': True,
                'message': 'Activity tracked successfully',
                'activity_id': activity_id
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to track activity'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_active_sessions_service(email):
    """Get all active sessions for a user - EXACT from line 2714"""
    try:
        active_sessions = list(activity_tracker.activities_collection.find(
            {"user_email": email, "is_active": True},
            {"_id": 0}
        ))
        
        return jsonify({
            'success': True,
            'user_email': email,
            'active_sessions': active_sessions,
            'count': len(active_sessions)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
