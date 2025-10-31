"""
Pregnancy Service - EXTRACTED FROM app_simple.py
Contains pregnancy tracking business logic - delegates to PregnancyService
EXACT SAME LOGIC - NO CHANGES
"""
from flask import jsonify, request
from app.shared.external_services.pregnancy_service import PregnancyService
from app.core.database import db

# Initialize
pregnancy_service = PregnancyService()


def get_pregnancy_week_service(week):
    """EXTRACTED FROM app_simple.py lines 7075-7086"""
    try:
        result = pregnancy_service.get_pregnancy_week_data(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_all_pregnancy_weeks_service():
    """EXTRACTED FROM app_simple.py lines 7088-7103"""
    try:
        weeks_data = pregnancy_service.get_all_pregnancy_weeks()
        return jsonify({
            'success': True,
            'data': {str(week): week_data.dict() for week, week_data in weeks_data.items()},
            'message': f'Successfully retrieved data for {len(weeks_data)} weeks'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_trimester_weeks_service(trimester):
    """EXTRACTED FROM app_simple.py lines 7105-7127"""
    try:
        if trimester not in [1, 2, 3]:
            return jsonify({
                'success': False,
                'message': 'Trimester must be 1, 2, or 3'
            }), 400
        
        weeks_data = pregnancy_service.get_trimester_weeks(trimester)
        return jsonify({
            'success': True,
            'trimester': trimester,
            'weeks': {str(week): week_data.dict() for week, week_data in weeks_data.items()},
            'message': f'Successfully retrieved weeks for trimester {trimester}'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_baby_size_image_service(week, style='matplotlib'):
    """EXTRACTED FROM app_simple.py lines 7129-7141"""
    try:
        result = pregnancy_service.get_baby_size_image(week, style)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


async def get_ai_baby_size_service(week):
    """EXTRACTED FROM app_simple.py lines 7143-7154"""
    try:
        result = await pregnancy_service.get_ai_baby_size(week)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


async def get_early_symptoms_service(week):
    """EXTRACTED FROM app_simple.py lines 7156-7167"""
    try:
        result = await pregnancy_service.get_early_symptoms(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


async def get_prenatal_screening_service(week):
    """EXTRACTED FROM app_simple.py lines 7169-7180"""
    try:
        result = await pregnancy_service.get_prenatal_screening(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


async def get_wellness_tips_service(week):
    """EXTRACTED FROM app_simple.py lines 7182-7193"""
    try:
        result = await pregnancy_service.get_wellness_tips(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


async def get_nutrition_tips_service(week):
    """EXTRACTED FROM app_simple.py lines 7195-7206"""
    try:
        result = await pregnancy_service.get_nutrition_tips(week)
        return jsonify(result.dict()), 200 if result.success else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_openai_status_service():
    """EXTRACTED FROM app_simple.py lines 7208-7219"""
    try:
        result = pregnancy_service.get_openai_status()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def save_pregnancy_tracking_service(patient_id, data):
    """EXTRACTED FROM app_simple.py lines 7221-7235"""
    try:
        result = pregnancy_service.save_pregnancy_tracking(patient_id, data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_pregnancy_tracking_history_service(patient_id):
    """EXTRACTED FROM app_simple.py lines 7237-7249"""
    try:
        result = pregnancy_service.get_pregnancy_tracking_history(patient_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def calculate_pregnancy_progress_service(patient_id):
    """EXTRACTED FROM app_simple.py lines 7251-7273"""
    try:
        result = pregnancy_service.calculate_pregnancy_progress(patient_id)
        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# ==================== KICK COUNT ENDPOINTS ====================
# EXTRACTED FROM app_simple.py lines 2732-2840

def save_kick_session_service(data, activity_tracker):
    """Save kick session data - EXACT from line 2732"""
    try:
        import json
        from datetime import datetime
        
        # Debug logging
        print(f"[*] Received kick session data: {json.dumps(data, indent=2)}")
        
        # Validate required fields
        required_fields = ['userId', 'userRole', 'kickCount', 'sessionDuration']
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
        
        print(f"[*] Looking for patient with ID: {patient_id}")
        
        # Find patient by Patient ID (more reliable than email)
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        
        print(f"[*] Found patient: {patient.get('username')} ({patient.get('email')})")
        
        # Create kick session entry
        kick_session_entry = {
            'kickCount': data['kickCount'],
            'sessionDuration': data['sessionDuration'],
            'sessionStartTime': data.get('sessionStartTime'),
            'sessionEndTime': data.get('sessionEndTime'),
            'averageKicksPerMinute': data.get('averageKicksPerMinute', 0),
            'notes': data.get('notes', ''),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'createdAt': datetime.now(),
        }
        
        # Add kick session to patient's kick_count_logs array using Patient ID
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"kick_count_logs": kick_session_entry},
                "$set": {"last_updated": datetime.now()}
            }
        )
        
        if result.modified_count > 0:
            # Log the kick session activity
            activity_tracker.log_activity(
                user_email=patient.get('email'),
                activity_type="kick_session_created",
                activity_data={
                    "kick_session_id": "embedded_in_patient_doc",
                    "kick_data": kick_session_entry,
                    "patient_id": patient_id,
                    "total_kick_sessions": len(patient.get('kick_count_logs', [])) + 1
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Kick session saved successfully to patient profile',
                'patientId': patient_id,
                'patientEmail': patient.get('email'),
                'kickSessionsCount': len(patient.get('kick_count_logs', [])) + 1
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save kick session to patient profile'}), 500
            
    except Exception as e:
        print(f"Error saving kick session: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_kick_history_service(patient_id):
    """Get kick history for a patient - EXACT from line 2816"""
    try:
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        
        # Get kick count logs
        kick_logs = patient.get('health_data', {}).get('kick_count_logs', [])
        
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'kick_logs': kick_logs,
            'total_sessions': len(kick_logs)
        }), 200
        
    except Exception as e:
        print(f"Error getting kick history: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_current_pregnancy_week_service(patient_id):
    """Get current pregnancy week - EXACT from line 2874"""
    try:
        from datetime import datetime
        print(f"[*] Getting current pregnancy week for patient ID: {patient_id}")
        
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        
        # Try to get pregnancy week from patient's health data
        pregnancy_week = 1  # Default fallback
        pregnancy_info = {}
        auto_fetched = False
        
        try:
            # First try to get pregnancy week directly from patient document
            if 'pregnancy_week' in patient:
                pregnancy_week = patient['pregnancy_week']
                auto_fetched = True
                print(f"[OK] Found pregnancy week in patient document: {pregnancy_week}")
            else:
                # Try to get from patient's health data
                health_data = patient.get('health_data', {})
                if 'pregnancy_week' in health_data:
                    pregnancy_week = health_data['pregnancy_week']
                    auto_fetched = True
                    print(f"[OK] Found pregnancy week in health data: {pregnancy_week}")
                else:
                    # Try to get from pregnancy info
                    pregnancy_info = health_data.get('pregnancy_info', {})
                    if pregnancy_info and 'current_week' in pregnancy_info:
                        pregnancy_week = pregnancy_info['current_week']
                        auto_fetched = True
                        print(f"[OK] Found pregnancy week in pregnancy info: {pregnancy_week}")
                    else:
                        print(f"[WARN] No pregnancy week found, using default: {pregnancy_week}")
        except Exception as e:
            print(f"[WARN] Error fetching pregnancy week: {e}, using default: {pregnancy_week}")
        
        print(f"[OK] Retrieved pregnancy week: {pregnancy_week} for patient: {patient_id}")
        
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'patientEmail': patient.get('email'),
            'current_pregnancy_week': pregnancy_week,
            'pregnancy_info': pregnancy_info,
            'auto_fetched': auto_fetched,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error getting current pregnancy week: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def update_patient_pregnancy_week_service(patient_id, data):
    """EXTRACTED FROM app_simple.py lines 2318-2376"""
    try:
        current_week = data.get('current_week')
        
        if not current_week:
            return jsonify({'error': 'current_week is required'}), 400
        
        # Update in database
        result = db.patients_collection.update_one(
            {'patient_id': patient_id},
            {'$set': {'current_pregnancy_week': current_week}}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'message': 'Pregnancy week updated successfully',
                'patient_id': patient_id,
                'current_week': current_week
            }), 200
        else:
            return jsonify({'error': 'Failed to update pregnancy week'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

