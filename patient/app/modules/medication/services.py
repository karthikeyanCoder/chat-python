"""
Medication Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 3937-6565
Business logic for medication management, OCR processing, N8N webhooks

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime, timedelta
from bson import ObjectId
import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from app.core.database import db
from app.shared.activity_tracker import activity_tracker
from app.shared.ocr_service import ocr_service


# Constants for better maintainability
class MedicationConstants:
    """Constants used throughout medication service"""
    # Status values
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_COMPLETED = 'completed'
    
    # Tracking types
    TYPE_DAILY_TRACKING = 'daily_tracking'
    TYPE_PRESCRIPTION = 'prescription'
    
    # Default confidence score
    DEFAULT_CONFIDENCE = 0.95
    
    # HTTP Status codes
    HTTP_OK = 200
    HTTP_BAD_REQUEST = 400
    HTTP_NOT_FOUND = 404
    HTTP_SERVER_ERROR = 500
    HTTP_SERVICE_UNAVAILABLE = 503


"""
Medication business logic service - CLASS-BASED MVC
Handles:
- Medication logging and history
- Prescription management and OCR processing
- Tablet tracking and reminders
- N8N webhook integration for AI processing
Dependencies injected via constructor for testability
"""
# HELPER FUNCTIONS
def _parse_medications_from_n8n_response(n8n_response):
    """Parse medications from N8N webhook response - EXACT from line 4455"""
    medications = []
    if not n8n_response:
        return medications
    try:
        print(f"[*] Parsing medications from N8N response: {n8n_response}")
        # Handle different response formats
        if isinstance(n8n_response, dict):
            # Look for medications in common N8N response fields
            if 'medications' in n8n_response:
                medications = n8n_response['medications']
            elif 'data' in n8n_response and 'medications' in n8n_response['data']:
                medications = n8n_response['data']['medications']
            elif 'result' in n8n_response and 'medications' in n8n_response['result']:
                medications = n8n_response['result']['medications']
            elif 'medication_list' in n8n_response:
                medications = n8n_response['medication_list']
            elif 'prescription' in n8n_response and 'medications' in n8n_response['prescription']:
                medications = n8n_response['prescription']['medications']
            else:
                # Try to find any array that might contain medications
                for key, value in n8n_response.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        # Check if this looks like medication data
                        if any(med_key in value[0] for med_key in ['medicationName', 'name', 'drug', 'medicine']):
                            medications = value
                            break
        # Ensure medications is a list
        if not isinstance(medications, list):
            medications = []
        # Normalize medication data structure
        normalized_medications = []
        for med in medications:
            if isinstance(med, dict):
                normalized_med = {
                    'medicationName': med.get('medicationName') or med.get('name') or med.get('drug') or med.get('medicine') or 'Unknown',
                    'purpose': med.get('purpose') or med.get('indication') or med.get('reason') or 'Not specified',
                    'dosage': med.get('dosage') or med.get('dose') or med.get('strength') or 'Not specified',
                    'route': med.get('route') or med.get('administration') or med.get('method') or 'oral',
                    'frequency': med.get('frequency') or med.get('schedule') or med.get('timing') or 'Not specified'
                }
                normalized_medications.append(normalized_med)
        print(f"[*] Parsed {len(normalized_medications)} medications from N8N response")
        # Debug: Print each medication
        for i, med in enumerate(normalized_medications, 1):
            print(f"  [*] Medication {i}: {med['medicationName']} - {med['purpose']} - {med['dosage']}")
        return normalized_medications
    except Exception as e:
        print(f"[ERROR] Error parsing medications from N8N response: {e}")
        return []
def _parse_medications_from_ocr(extracted_text):
    """Parse medications from OCR extracted text - EXACT from line 4516"""
    medications = []
    if not extracted_text:
        return medications
    try:
        # Split text into lines for processing
        lines = extracted_text.split('\n')
        # Look for medication patterns
        current_medication = {}
        in_medication_section = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check if we're in a medication section
            if any(keyword in line.lower() for keyword in ['medication', 'medicine', 'drug', 'prescription']):
                in_medication_section = True
                continue
            # If we're in medication section, try to parse medication data
            if in_medication_section:
                # Look for medication name patterns
                if any(keyword in line.lower() for keyword in ['tablet', 'mg', 'ml', 'capsule', 'syrup', 'injection']):
                    # This might be a medication line
                    parts = line.split()
                    # Try to extract medication information
                    medication = {
                        'medicationName': '',
                        'purpose': '',
                        'dosage': '',
                        'route': '',
                        'frequency': ''
                    }
                    # Simple parsing logic - can be enhanced
                    for i, part in enumerate(parts):
                        if part.lower() in ['tablet', 'capsule', 'syrup', 'injection']:
                            # Found medication type
                            if i > 0:
                                medication['medicationName'] = ' '.join(parts[:i+1])
                            break
                        elif 'mg' in part or 'ml' in part:
                            medication['dosage'] = part
                        elif part.lower() in ['oral', 'topical', 'injection', 'inhalation']:
                            medication['route'] = part
                        elif any(freq in part.lower() for freq in ['daily', 'twice', 'thrice', 'hourly', 'weekly']):
                            medication['frequency'] = part
                    # If we found a medication name, add it
                    if medication['medicationName']:
                        medications.append(medication)
                        current_medication = {}
        # If no medications found with the above method, try a simpler approach
        if not medications:
            # Look for common medication patterns
            medication_patterns = [
                r'([A-Za-z\s]+)\s+(\d+\s*(?:mg|ml|g))\s+(?:oral|tablet|capsule)',
                r'([A-Za-z\s]+)\s+(?:for|to treat)\s+([A-Za-z\s]+)',
            ]
            for pattern in medication_patterns:
                matches = re.findall(pattern, extracted_text, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 2:
                        medication = {
                            'medicationName': match[0].strip(),
                            'purpose': match[1].strip() if len(match) > 1 else '',
                            'dosage': '',
                            'route': 'oral',
                            'frequency': ''
                        }
                        medications.append(medication)
        # If still no medications found, create a default one
        if not medications:
            medications.append({
                'medicationName': 'Prescription Document',
                'purpose': 'As prescribed by doctor',
                'dosage': 'As directed',
                'route': 'oral',
                'frequency': 'As needed'
            })
        print(f"[*] Parsed {len(medications)} medications from OCR text")
        return medications
    except Exception as e:
        print(f"[ERROR] Error parsing medications: {e}")
        return [{
            'medicationName': 'Prescription Document',
            'purpose': 'As prescribed by doctor',
            'dosage': 'As directed',
            'route': 'oral',
            'frequency': 'As needed'
        }]
# BASIC MEDICATION MANAGEMENT ENDPOINTS
def save_medication_log_service(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Save medication log to patient profile - EXACT from line 3937
    Args:
        data: Dictionary containing medication log details
              Required: patient_id, medication_name
              Optional: dosages, prescription_details, notes, etc.
    Returns:
        Tuple of (response_dict, http_status_code)
    """
    try:
        # Debug logging
        print(f"[*] Received medication log data: {json.dumps(data, indent=2)}")
        print(f"[*] Data keys: {list(data.keys())}")
        print(f"[*] Dosages field: {data.get('dosages', 'NOT_FOUND')}")
        print(f"[*] Is prescription mode: {data.get('is_prescription_mode', 'NOT_FOUND')}")
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        # Validate required fields
        required_fields = ['patient_id', 'medication_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        patient_id = data.get('patient_id')
        medication_name = data.get('medication_name', '').strip()
        if not medication_name:
            return jsonify({
                'success': False,
                'message': 'Medication name is required'
            }), 400
        # Check if it's prescription mode or multiple dosages mode
        is_prescription_mode = data.get('is_prescription_mode', False)
        dosages = data.get('dosages', [])
        prescription_details = data.get('prescription_details', '').strip()
        # Ensure dosages is always a list
        if not isinstance(dosages, list):
            print(f"[WARN] Warning: dosages is not a list, converting from {type(dosages)}")
            dosages = []
        print(f"[*] Validation Debug:")
        print(f"[*] - Is prescription mode: {is_prescription_mode}")
        print(f"[*] - Dosages type: {type(dosages)}")
        print(f"[*] - Dosages length: {len(dosages) if isinstance(dosages, list) else 'NOT_A_LIST'}")
        print(f"[*] - Dosages content: {dosages}")
        print(f"[*] - Prescription details: '{prescription_details}'")
        # Handle backward compatibility with old format
        if not is_prescription_mode and len(dosages) == 0:
            # Check for old format fields
            old_dosage = data.get('dosage', '').strip()
            old_time_taken = data.get('time_taken', '').strip()
            if old_dosage and old_time_taken:
                # Convert old format to new format
                dosages = [{
                    'dosage': old_dosage,
                    'time': old_time_taken,
                    'frequency': 'As prescribed',
                    'reminder_enabled': False,
                    'next_dose_time': None,
                    'special_instructions': ''
                }]
                print(f"[*] Converted old format to new format: {dosages}")
            else:
                return jsonify({
                    'success': False,
                    'message': 'At least one dosage is required when not in prescription mode'
                }), 400
        if is_prescription_mode:
            if not prescription_details:
                return jsonify({
                    'success': False,
                    'message': 'Prescription details are required in prescription mode'
                }), 400
        elif len(dosages) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one dosage is required when not in prescription mode'
            }), 400
        print(f"[*] Looking for patient with ID: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        print(f"[*] Found patient: {patient.get('username')} ({patient.get('email')})")
        # Create medication log entry
        medication_log_entry = {
            'medication_name': medication_name,
            'date_taken': data.get('date_taken', datetime.now().strftime('%d/%m/%Y')),
            'timestamp': datetime.now().isoformat(),
            'createdAt': datetime.now(),
            'pregnancy_week': patient.get('pregnancy_week', 1),
            'trimester': 'First' if patient.get('pregnancy_week', 1) <= 12 else 'Second' if patient.get('pregnancy_week', 1) <= 26 else 'Third',
            'notes': data.get('notes', ''),
            'prescribed_by': data.get('prescribed_by', ''),
            'medication_type': data.get('medication_type', 'prescription'),
            'side_effects': data.get('side_effects', []),
            'is_prescription_mode': is_prescription_mode,
            'prescription_details': prescription_details,
            'dosages': dosages,
            'total_dosages': len(dosages) if not is_prescription_mode else 0
        }
        # Add medication log to patient's medication_logs array
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"medication_logs": medication_log_entry},
                "$set": {"last_updated": datetime.now()}
            }
        )
        if result.modified_count > 0:
            # Log the medication activity
            activity_tracker.log_activity(
                user_email=patient.get('email'),
                activity_type="medication_log_created",
                activity_data={
                    "medication_log_id": "embedded_in_patient_doc",
                    "medication_data": medication_log_entry,
                    "patient_id": patient_id,
                    "total_medication_logs": len(patient.get('medication_logs', [])) + 1,
                    "is_prescription_mode": is_prescription_mode,
                    "total_dosages": len(dosages) if not is_prescription_mode else 0
                }
            )
            return jsonify({
                'success': True,
                'message': 'Medication log saved successfully',
                'patientId': patient_id,
                'patientEmail': patient.get('email'),
                'medicationLogsCount': len(patient.get('medication_logs', [])) + 1,
                'timestamp': medication_log_entry['timestamp']
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save medication log'}), 500
    except Exception as e:
        print(f"Error saving medication log: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def get_medication_history_service(patient_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get medication history for a patient - EXACT from line 4091
    Args:
        patient_id: Patient identifier
    Returns:
        Tuple of (response_dict with medication logs, http_status_code)
    """
    try:
        print(f"[*] Getting medication history for patient ID: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Get medication logs from patient document
        medication_logs = patient.get('medication_logs', [])
        # Sort by newest first
        medication_logs.sort(key=lambda x: x.get('createdAt', datetime.min), reverse=True)
        # Convert datetime objects to strings for JSON serialization
        for entry in medication_logs:
            if 'createdAt' in entry:
                if isinstance(entry['createdAt'], datetime):
                    entry['createdAt'] = entry['createdAt'].isoformat()
        print(f"[OK] Retrieved {len(medication_logs)} medication logs for patient: {patient_id}")
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'medication_logs': medication_logs,
            'totalEntries': len(medication_logs)
        }), 200
    except Exception as e:
        print(f"Error getting medication history: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def get_upcoming_dosages_service(patient_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get upcoming dosages and alerts for a patient - EXACT from line 4126
    Args:
        patient_id: Patient identifier
    Returns:
        Tuple of (response_dict with upcoming dosages, http_status_code)
    """
    try:
        print(f"[*] Getting upcoming dosages for patient ID: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Get medication logs from patient document
        medication_logs = patient.get('medication_logs', [])
        # Process dosages and create upcoming schedule
        upcoming_dosages = []
        today = datetime.now()
        for log in medication_logs:
            if not log.get('is_prescription_mode', False):
                # Handle multiple dosages
                dosages = log.get('dosages', [])
                for dosage in dosages:
                    if dosage.get('reminder_enabled', False):
                        # Parse time and create schedule
                        try:
                            time_str = dosage.get('time', '')
                            if time_str:
                                hour, minute = map(int, time_str.split(':'))
                                next_dose = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
                                # If time has passed today, schedule for tomorrow
                                if next_dose < today:
                                    next_dose += timedelta(days=1)
                                upcoming_dosages.append({
                                    'medication_name': log.get('medication_name', 'Unknown'),
                                    'dosage': dosage.get('dosage', ''),
                                    'time': time_str,
                                    'frequency': dosage.get('frequency', ''),
                                    'next_dose_time': next_dose.isoformat(),
                                    'special_instructions': dosage.get('special_instructions', ''),
                                    'medication_type': log.get('medication_type', 'prescription'),
                                    'prescribed_by': log.get('prescribed_by', ''),
                                    'notes': log.get('notes', ''),
                                    'urgency_level': 'normal'
                                })
                        except Exception as e:
                            print(f"[WARN] Error parsing dosage time: {e}")
                            continue
        # Sort by next dose time
        upcoming_dosages.sort(key=lambda x: x.get('next_dose_time', ''))
        # Add prescription mode medications as general reminders
        prescription_medications = []
        for log in medication_logs:
            if log.get('is_prescription_mode', False):
                prescription_medications.append({
                    'medication_name': log.get('medication_name', 'Unknown'),
                    'type': 'prescription',
                    'details': log.get('prescription_details', ''),
                    'prescribed_by': log.get('prescribed_by', ''),
                    'notes': log.get('notes', ''),
                    'urgency_level': 'normal'
                })
        print(f"[OK] Retrieved {len(upcoming_dosages)} upcoming dosages and {len(prescription_medications)} prescription medications for patient: {patient_id}")
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'upcoming_dosages': upcoming_dosages,
            'prescription_medications': prescription_medications,
            'total_upcoming': len(upcoming_dosages),
            'total_prescriptions': len(prescription_medications),
            'current_time': today.isoformat()
        }), 200
    except Exception as e:
        print(f"Error getting upcoming dosages: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def save_tablet_taken_service(data):
    """Save daily tablet tracking for a patient - EXACT from line 4209"""
    try:
        print(f"[*] Saving tablet taken: {data}")
        # Validate required fields
        required_fields = ['patient_id', 'tablet_name', 'date_taken']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        patient_id = data['patient_id']
        tablet_name = data['tablet_name']
        notes = data.get('notes', '')
        date_taken = data['date_taken']
        time_taken = data.get('time_taken', datetime.now().isoformat())
        tracking_type = data.get('type', 'daily_tracking')
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Create tablet tracking entry
        tablet_entry = {
            'tablet_name': tablet_name,
            'notes': notes,
            'date_taken': date_taken,
            'time_taken': time_taken,
            'type': tracking_type,
            'timestamp': datetime.now().isoformat()
        }
        # Add to patient's tablet tracking history
        if 'tablet_tracking' not in patient:
            patient['tablet_tracking'] = []
        patient['tablet_tracking'].append(tablet_entry)
        # Update patient document
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"tablet_tracking": patient['tablet_tracking']}}
        )
        if result.modified_count > 0:
            print(f"[OK] Tablet tracking saved successfully for patient: {patient_id}")
            return jsonify({
                'success': True,
                'message': f'Tablet "{tablet_name}" tracking saved successfully',
                'tablet_entry': tablet_entry
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save tablet tracking'}), 500
    except Exception as e:
        print(f"Error saving tablet tracking: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def get_tablet_history_service(patient_id):
    """Get tablet tracking history for a patient - EXACT from line 4270"""
    try:
        print(f"[*] Getting tablet history for patient ID: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Get tablet tracking history
        tablet_history = patient.get('tablet_tracking', [])
        # Sort by timestamp (most recent first)
        tablet_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        print(f"[OK] Retrieved {len(tablet_history)} tablet tracking entries for patient: {patient_id}")
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'tablet_history': tablet_history,
            'totalEntries': len(tablet_history)
        }), 200
    except Exception as e:
        print(f"Error getting tablet history: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def upload_prescription_service(data):
    """Upload prescription details and dosage information - EXACT from line 4300"""
    try:
        print("[*] Uploading prescription details...")
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        # Validate required fields
        required_fields = ['patient_id', 'medication_name', 'prescription_details']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        patient_id = data['patient_id']
        medication_name = data['medication_name']
        prescription_details = data['prescription_details']
        prescribed_by = data.get('prescribed_by', '')
        medication_type = data.get('medication_type', 'prescription')
        dosage_instructions = data.get('dosage_instructions', '')
        frequency = data.get('frequency', '')
        duration = data.get('duration', '')
        special_instructions = data.get('special_instructions', '')
        pregnancy_week = data.get('pregnancy_week', 0)
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Create prescription entry
        prescription_entry = {
            'medication_name': medication_name,
            'prescription_details': prescription_details,
            'prescribed_by': prescribed_by,
            'medication_type': medication_type,
            'dosage_instructions': dosage_instructions,
            'frequency': frequency,
            'duration': duration,
            'special_instructions': special_instructions,
            'pregnancy_week': pregnancy_week,
            'upload_date': datetime.now().isoformat(),
            'status': 'active'
        }
        # Add to patient's prescription history
        if 'prescriptions' not in patient:
            patient['prescriptions'] = []
        patient['prescriptions'].append(prescription_entry)
        # Update patient document
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"prescriptions": patient['prescriptions']}}
        )
        if result.modified_count > 0:
            print(f"[OK] Prescription uploaded successfully for patient: {patient_id}")
            return jsonify({
                'success': True,
                'message': f'Prescription for "{medication_name}" uploaded successfully',
                'prescription_entry': prescription_entry
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to upload prescription'}), 500
    except Exception as e:
        print(f"Error uploading prescription: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def get_prescription_details_service(patient_id):
    """Get prescription details and dosage information - EXACT from line 4373"""
    try:
        print(f"[*] Getting prescription details for patient ID: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Get prescription details
        prescriptions = patient.get('prescriptions', [])
        # Sort by upload date (most recent first)
        prescriptions.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        # Get active prescriptions only
        active_prescriptions = [p for p in prescriptions if p.get('status') == 'active']
        print(f"[OK] Retrieved {len(active_prescriptions)} active prescriptions for patient: {patient_id}")
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'prescriptions': active_prescriptions,
            'totalPrescriptions': len(active_prescriptions),
            'allPrescriptions': prescriptions
        }), 200
    except Exception as e:
        print(f"Error getting prescription details: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def update_prescription_status_service(patient_id, prescription_id, data):
    """Update prescription status (active/inactive/completed) - EXACT from line 4407"""
    try:
        print(f"[*] Updating prescription status for patient ID: {patient_id}, prescription ID: {prescription_id}")
        if not data or 'status' not in data:
            return jsonify({'success': False, 'message': 'Status field is required'}), 400
        new_status = data['status']
        valid_statuses = ['active', 'inactive', 'completed']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        # Find patient and update prescription status
        result = db.patients_collection.update_one(
            {
                "patient_id": patient_id,
                "prescriptions._id": prescription_id
            },
            {
                "$set": {
                    "prescriptions.$.status": new_status,
                    "prescriptions.$.last_updated": datetime.now().isoformat()
                }
            }
        )
        if result.modified_count > 0:
            print(f"[OK] Prescription status updated successfully for patient: {patient_id}")
            return jsonify({
                'success': True,
                'message': f'Prescription status updated to {new_status}',
                'patientId': patient_id,
                'prescriptionId': prescription_id,
                'newStatus': new_status
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Prescription not found or no changes made'}), 404
    except Exception as e:
        print(f"Error updating prescription status: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
# ==================== OCR PROCESSING METHODS ====================
# EXTRACTED FROM app_simple.py lines 4623-6565
# EXACT code - NO changes to business logic
def process_prescription_document_ocr_service(file, patient_id, medication_name,
                                      enhanced_ocr_service, ocr_service,
                                      webhook_service, OCR_SERVICES_AVAILABLE,
                                      PYMUPDF_AVAILABLE, PIL_AVAILABLE, DEFAULT_WEBHOOK_URL):
    """Process prescription document using PaddleOCR service - EXACT from line 4623"""
    try:
        print("[*] Processing prescription document with PaddleOCR...")
        # Check if file is present
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        print(f"[*] Processing file: {file.filename}")
        print(f"[*] Patient ID: {patient_id}")
        print(f"[*] Medication Name: {medication_name}")
        # Read file content
        file_content = file.read()
        # Use medication folder's enhanced OCR service if available, otherwise fallback to basic OCR
        if enhanced_ocr_service and OCR_SERVICES_AVAILABLE:
            print("[*] Using medication folder's enhanced OCR service...")
            # Validate file type with enhanced service
            if not enhanced_ocr_service.validate_file_type(file.content_type, file.filename):
                return jsonify({
                    'success': False,
                    'message': f'Unsupported file type: {file.content_type}. Supported types: {enhanced_ocr_service.allowed_types}'
                }), 400
            # Process with enhanced OCR service from medication folder
            import asyncio
            try:
                # Create event loop for async OCR service
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                ocr_result = loop.run_until_complete(
                    enhanced_ocr_service.process_file(
                        file_content=file_content,
                        filename=file.filename
                    )
                )
                loop.close()
                print("[OK] Medication folder OCR processing successful")
                # Extract full text content in the format expected by medication folder
                if ocr_result.get('success'):
                    # Get the full text content from the medication folder service
                    full_text_content = ocr_result.get('full_content', '')
                    if not full_text_content and ocr_result.get('results'):
                        # Build full text content from results if not provided
                        full_text_content = ""
                        for i, result in enumerate(ocr_result['results'], 1):
                            text = result.get('text', '')
                            confidence = result.get('confidence', 0)
                            confidence_percent = f"{confidence * 100:.2f}%"
                            full_text_content += f"Text {i}: {text} (Confidence: {confidence_percent})\n"
                        full_text_content = full_text_content.strip()
                    # Update OCR result with full text content
                    ocr_result['full_text_content'] = full_text_content
                    ocr_result['extracted_text'] = full_text_content  # For backward compatibility
            except Exception as e:
                print(f"[WARN] Medication folder OCR service error, falling back to basic OCR: {e}")
                if ocr_service:
                    ocr_result = ocr_service.process_file(file_content, file.filename)
                else:
                    return jsonify({'success': False, 'message': 'OCR service not available'}), 503
        elif ocr_service:
            print("[WARN] Using basic OCR service (medication folder not available)")
            # Validate file type with basic service
            if not ocr_service.validate_file_type(file.content_type, file.filename):
                return jsonify({
                    'success': False,
                    'message': f'Unsupported file type: {file.content_type}. Supported types: {list(ocr_service.supported_formats.keys())}'
                }), 400
            ocr_result = ocr_service.process_file(file_content, file.filename)
        else:
            print("[*] Using basic OCR fallback (no PaddleOCR available)...")
            # Basic OCR fallback implementation
            file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            full_text = ""
            results = []
            try:
                if file_extension == 'pdf' and PYMUPDF_AVAILABLE:
                    print("[*] Processing PDF with PyMuPDF...")
                    import fitz
                    pdf_document = fitz.open(stream=file_content, filetype="pdf")
                    full_text = ""
                    for page_num in range(len(pdf_document)):
                        page = pdf_document[page_num]
                        page_text = page.get_text()
                        if page_text.strip():
                            full_text += page_text + "\n"
                            results.append({
                                "page": page_num + 1,
                                "text": page_text.strip(),
                                "method": "native_pdf",
                                "confidence": 1.0
                            })
                    pdf_document.close()
                elif file_extension in ['txt']:
                    print("[*] Processing text file...")
                    full_text = file_content.decode('utf-8', errors='ignore')
                    lines = full_text.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip():
                            results.append({
                                "line": i + 1,
                                "text": line.strip(),
                                "method": "native_text",
                                "confidence": 1.0
                            })
                elif file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'tiff'] and PIL_AVAILABLE:
                    print("[*] Processing image file (basic extraction)...")
                    from PIL import Image
                    import io
                    image = Image.open(io.BytesIO(file_content))
                    # For now, just return basic info - would need OCR library for actual text extraction
                    full_text = f"Image file: {file.filename} (OCR not available - install PaddleOCR for text extraction)"
                    results.append({
                        "text": full_text,
                        "method": "image_placeholder",
                        "confidence": 0.0
                    })
                else:
                    print(f"[WARN] Unsupported file type: {file_extension}")
                    return jsonify({
                        'success': False,
                        'message': f'Unsupported file type: {file_extension}. Supported types: pdf, txt, jpg, png, bmp, tiff'
                    }), 400
                # Create OCR result in expected format
                ocr_result = {
                    'success': True,
                    'filename': file.filename,
                    'file_type': file.content_type,
                    'extracted_text': full_text,
                    'full_content': full_text,
                    'results': results,
                    'total_pages': len([r for r in results if 'page' in r]) or 1,
                    'native_text_pages': len([r for r in results if r.get('method') in ['native_pdf', 'native_text']]),
                    'ocr_pages': len([r for r in results if r.get('method') == 'image_placeholder'])
                }
            except Exception as e:
                print(f"[ERROR] Basic OCR processing failed: {e}")
                return jsonify({
                    'success': False,
                    'message': f'OCR processing failed: {str(e)}'
                }), 500
        if not ocr_result['success']:
            return jsonify({
                'success': False,
                'message': f'OCR processing failed: {ocr_result["error"]}'
            }), 500
        # Extract the processed text
        extracted_text = ocr_result.get('extracted_text', '')
        if not extracted_text or extracted_text.strip() == '':
            return jsonify({
                'success': False,
                'message': 'No text could be extracted from the document'
            }), 400
        print(f"[OK] Successfully extracted text from {file.filename}")
        print(f"[*] Extracted text length: {len(extracted_text)} characters")
        # Store in database
        prescription_data = {
            'patient_id': patient_id,
            'medication_name': medication_name,
            'filename': file.filename,
            'file_type': file.content_type,
            'processed_at': datetime.now(),
            'ocr_result': ocr_result,
            'extracted_text': extracted_text,
            'text_elements': ocr_result.get('results', []),
            'processing_method': 'paddleocr_enhanced' if enhanced_ocr_service and OCR_SERVICES_AVAILABLE else 'basic_fallback'
        }
        # Save to database
        if db.patients_collection is not None:
            db.patients_collection.update_one(
                {"patient_id": patient_id},
                {"$push": {"prescription_documents": prescription_data}},
                upsert=True
            )
            print(f"[*] Prescription data saved to database for patient {patient_id}")
        # Send results to N8N webhook if processing was successful
        webhook_results = []
        print(f"[*] Webhook service available: {webhook_service is not None}")
        if webhook_service:
            print(f"[*] Webhook service configured: {webhook_service.is_configured()}")
        # Always try to send webhook if OCR was successful
        webhook_success = False
        n8n_response_data = None
        if ocr_result.get("success"):
            print("[*] Sending OCR results to N8N webhook...")
            # Prepare webhook data in the correct format
            webhook_data = {
                'success': True,
                'patient_id': patient_id,
                'medication_name': medication_name,
                'filename': file.filename,
                'extracted_text': ocr_result.get('extracted_text', ''),
                'full_content': ocr_result.get('full_content', ''),
                'file_type': ocr_result.get('file_type', ''),
                'total_pages': ocr_result.get('total_pages', 1),
                'processing_method': ocr_result.get('processing_method', 'paddleocr'),
                'timestamp': datetime.now().isoformat(),
                'results': ocr_result.get('results', [])
            }
            # Send webhook only once - try webhook service first, then direct call if needed
            import asyncio
            if webhook_service:
                try:
                    print("[*] Using webhook service...")
                    # Create new event loop for webhook service
                    webhook_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(webhook_loop)
                    webhook_results = webhook_loop.run_until_complete(
                        webhook_service.send_ocr_result(webhook_data, file.filename)
                    )
                    webhook_loop.close()
                    # Check if any webhook was successful and capture response
                    if webhook_results:
                        for webhook_result in webhook_results:
                            if webhook_result["success"]:
                                print(f"[OK] N8N Webhook sent successfully to {webhook_result['config_name']} ({webhook_result['url']})")
                                # Capture N8N response data if available
                                if 'response_data' in webhook_result:
                                    n8n_response_data = webhook_result['response_data']
                                    print(f"[*] N8N Response data captured: {n8n_response_data}")
                                    print(f"[*] N8N Response type: {type(n8n_response_data)}")
                                    if isinstance(n8n_response_data, dict):
                                        print(f"[*] N8N Response keys: {list(n8n_response_data.keys())}")
                                webhook_success = True
                                break  # Stop after first success
                            else:
                                print(f"[ERROR] N8N Webhook failed for {webhook_result['config_name']}: {webhook_result.get('error', 'Unknown error')}")
                    if not webhook_success:
                        print("[WARN] No successful webhook results from webhook service, trying direct call...")
                except Exception as e:
                    print(f"[ERROR] Webhook service failed: {e}")
                    print("[WARN] Trying direct call as fallback...")
            # Only try direct call if webhook service didn't succeed
            if not webhook_success:
                try:
                    print("[*] Sending direct N8N webhook call...")
                    n8n_url = DEFAULT_WEBHOOK_URL
                    print(f"[*] Using webhook URL: {n8n_url}")
                    import requests
                    response = requests.post(
                        n8n_url,
                        json=webhook_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    if response.status_code == 200:
                        print("[OK] Direct N8N webhook call successful!")
                        # Try to parse N8N response data
                        try:
                            n8n_response_data = response.json()
                            print(f"[*] N8N Response data captured: {n8n_response_data}")
                            print(f"[*] N8N Response type: {type(n8n_response_data)}")
                            if isinstance(n8n_response_data, dict):
                                print(f"[*] N8N Response keys: {list(n8n_response_data.keys())}")
                        except:
                            n8n_response_data = response.text
                            print(f"[*] N8N Response text captured: {n8n_response_data}")
                            print(f"[*] N8N Response type: {type(n8n_response_data)}")
                        webhook_success = True
                        webhook_results = [{
                            'success': True,
                            'config_name': 'Direct N8N Call',
                            'url': n8n_url,
                            'response_status': response.status_code,
                            'response_data': n8n_response_data
                        }]
                    else:
                        print(f"[ERROR] Direct N8N webhook failed: {response.status_code} - {response.text}")
                        webhook_results = [{
                            'success': False,
                            'config_name': 'Direct N8N Call',
                            'url': n8n_url,
                            'error': f"HTTP {response.status_code}: {response.text}"
                        }]
                except Exception as direct_error:
                    print(f"[ERROR] Direct N8N webhook call failed: {direct_error}")
                    webhook_results = [{
                        'success': False,
                        'config_name': 'Direct N8N Call',
                        'url': n8n_url,
                        'error': str(direct_error)
                    }]
            else:
                print("[OK] Webhook already successful, skipping direct call")
        else:
            print("[WARN] OCR processing failed, skipping webhook")
            webhook_results = []
        # Return the extracted text and N8N webhook results for the user to review
        return jsonify({
            'success': True,
            'message': 'Document processed successfully' + (' with PaddleOCR' if enhanced_ocr_service and OCR_SERVICES_AVAILABLE else ' with basic OCR'),
            'filename': file.filename,
            'file_type': ocr_result['file_type'],
            'extracted_text': extracted_text,
            'total_pages': ocr_result.get('total_pages', 1),
            'native_text_pages': ocr_result.get('native_text_pages', 0),
            'ocr_pages': ocr_result.get('ocr_pages', 0),
            'processing_details': {
                'method': 'paddleocr_extraction' if enhanced_ocr_service and OCR_SERVICES_AVAILABLE else 'basic_ocr_extraction',
                'confidence': ocr_result.get('results', [{}])[0].get('confidence', 0.0) if ocr_result.get('results') else 0.0,
                'service_used': 'PaddleOCR Enhanced' if enhanced_ocr_service and OCR_SERVICES_AVAILABLE else 'Basic OCR'
            },
            'n8n_webhook_results': {
                'webhook_success': webhook_success,
                'webhook_calls': webhook_results,
                'total_calls': len(webhook_results),
                'successful_calls': len([r for r in webhook_results if r.get('success', False)]),
                'failed_calls': len([r for r in webhook_results if not r.get('success', False)])
            },
            'n8n_response_data': n8n_response_data,
            'parsed_medications': _parse_medications_from_n8n_response(n8n_response_data) if n8n_response_data else _parse_medications_from_ocr(extracted_text)
        }), 200
    except Exception as e:
        print(f"[ERROR] Error processing prescription document: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def process_with_paddleocr_service(file, patient_id, medication_name,
                            enhanced_ocr_service, OCR_SERVICES_AVAILABLE):
    """Process prescription using medication folder's PaddleOCR - EXACT from line 4989"""
    try:
        print("[*] Processing prescription with medication folder PaddleOCR service...")
        if not enhanced_ocr_service or not OCR_SERVICES_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'PaddleOCR service not available (paddlepaddle not installed)'
            }), 503
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        print(f"[*] Processing file: {file.filename}")
        print(f"[*] Patient ID: {patient_id}")
        print(f"[*] Medication Name: {medication_name}")
        # Validate file type with enhanced service
        if not enhanced_ocr_service.validate_file_type(file.content_type, file.filename):
            return jsonify({
                'success': False,
                'message': f'Unsupported file type: {file.content_type}. Supported types: {enhanced_ocr_service.allowed_types}'
            }), 400
        # Read file content
        file_content = file.read()
        try:
            # Create event loop for async OCR service
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ocr_result = loop.run_until_complete(
                enhanced_ocr_service.process_file(
                    file_content=file_content,
                    filename=file.filename
                )
            )
            loop.close()
            print("[OK] Medication folder OCR processing successful")
            print(f"[*] Debug - OCR result keys: {list(ocr_result.keys())}")
            print(f"[*] Debug - OCR result success: {ocr_result.get('success')}")
            # Extract full text content in the format expected by medication folder
            if ocr_result.get('success'):
                # Get the full text content from the medication folder service
                full_text_content = ocr_result.get('full_content', '')
                print(f"[*] Debug - full_content from OCR: '{full_text_content}'")
                print(f"[*] Debug - full_content length: {len(full_text_content)}")
                # If full_content is not available, extract from results
                if not full_text_content and ocr_result.get('results'):
                    print(f"[*] Debug - Extracting from results: {len(ocr_result['results'])} results")
                    # Extract all text from results and combine them
                    extracted_texts = []
                    for result in ocr_result['results']:
                        text = result.get('text', '').strip()
                        if text:  # Only add non-empty text
                            extracted_texts.append(text)
                    # Combine all extracted text into one continuous string
                    full_text_content = ' '.join(extracted_texts)
                    print(f"[*] Debug - Combined text from results: '{full_text_content}'")
                    # If still no content, try alternative fields
                    if not full_text_content:
                        full_text_content = ocr_result.get('extracted_text', '')
                        print(f"[*] Debug - Trying extracted_text: '{full_text_content}'")
                    # If still no content, try the raw text field
                    if not full_text_content:
                        full_text_content = ocr_result.get('text', '')
                        print(f"[*] Debug - Trying text field: '{full_text_content}'")
                # If we still don't have content, create a fallback
                if not full_text_content:
                    full_text_content = "No text could be extracted from the document"
                    print(f"[*] Debug - Using fallback text")
                # Update OCR result with full text content
                ocr_result['full_text_content'] = full_text_content
                ocr_result['extracted_text'] = full_text_content  # For backward compatibility
                print(f"[*] Debug - Final full_text_content: '{full_text_content}'")
                print(f"[*] Debug - Final full_text_content length: {len(full_text_content)}")
            else:
                print(f"[*] Debug - OCR processing failed: {ocr_result.get('error', 'Unknown error')}")
            # Placeholder for webhook_results (would be populated by webhook service)
            webhook_results = []
            # Return comprehensive result with full text content
            final_response = {
                'success': True,
                'message': 'Document processed successfully with medication folder OCR service',
                'filename': file.filename,
                'ocr_result': ocr_result,
                'full_text_content': ocr_result.get('full_text_content', ''),
                'webhook_delivery': {
                    'status': 'completed' if webhook_results else 'not_configured',
                    'results': webhook_results,
                    'timestamp': datetime.now().isoformat()
                },
                'service_used': 'Medication Folder Enhanced OCR',
                'timestamp': datetime.now().isoformat()
            }
            print(f"[*] Debug - Final response full_text_content: '{final_response['full_text_content']}'")
            print(f"[*] Debug - Final response full_text_content length: {len(final_response['full_text_content'])}")
            print(f"[*] Debug - Final response keys: {list(final_response.keys())}")
            return jsonify(final_response), 200
        except Exception as e:
            print(f"[ERROR] PaddleOCR processing error: {e}")
            return jsonify({
                'success': False,
                'message': f'PaddleOCR processing failed: {str(e)}'
            }), 500
    except Exception as e:
        print(f"[ERROR] Error in process_with_paddleocr: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def process_prescription_text_service(data):
    """Process raw prescription text - EXACT from line 5124"""
    try:
        print("[*] Processing prescription text for structured extraction...")
        if not data or 'text' not in data:
            return jsonify({'success': False, 'message': 'Text content is required'}), 400
        prescription_text = data['text']
        patient_id = data.get('patient_id', '')
        print(f"[*] Processing text for patient: {patient_id}")
        print(f"[*] Text length: {len(prescription_text)} characters")
        # Basic text processing and cleaning
        cleaned_text = prescription_text.strip()
        # Extract potential medication information using simple patterns
        extracted_info = {
            'medication_name': '',
            'dosage': '',
            'frequency': '',
            'duration': '',
            'instructions': '',
            'prescribed_by': '',
            'raw_text': cleaned_text
        }
        # Simple pattern matching for common prescription formats
        lines = cleaned_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Look for medication name patterns
            if any(keyword in line.lower() for keyword in ['tablet', 'capsule', 'syrup', 'injection', 'mg', 'ml']):
                if not extracted_info['medication_name']:
                    extracted_info['medication_name'] = line
            # Look for dosage patterns
            elif any(keyword in line.lower() for keyword in ['mg', 'ml', 'tablet', 'capsule', 'dose']):
                if not extracted_info['dosage']:
                    extracted_info['dosage'] = line
            # Look for frequency patterns
            elif any(keyword in line.lower() for keyword in ['daily', 'twice', 'three times', 'every', 'hour']):
                if not extracted_info['frequency']:
                    extracted_info['frequency'] = line
            # Look for duration patterns
            elif any(keyword in line.lower() for keyword in ['days', 'weeks', 'months', 'until', 'course']):
                if not extracted_info['duration']:
                    extracted_info['duration'] = line
        print(f"[OK] Successfully processed prescription text")
        return jsonify({
            'success': True,
            'message': 'Prescription text processed successfully',
            'extracted_info': extracted_info,
            'processing_details': {
                'method': 'text_analysis',
                'confidence': 0.7,
                'total_lines_processed': len(lines)
            }
        }), 200
    except Exception as e:
        print(f"[ERROR] Error processing prescription text: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def process_with_mock_n8n_service(data, webhook_service, mock_n8n_service):
    """Process prescription with N8N webhook - EXACT from line 5199"""
    try:
        print("[*] Processing prescription with N8N webhook...")
        patient_id = data.get('patient_id')
        medication_name = data.get('medication_name')
        extracted_text = data.get('extracted_text')
        filename = data.get('filename')
        if not patient_id or not extracted_text:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        print(f"[*] Processing for patient: {patient_id}")
        print(f"[*] Medication: {medication_name}")
        print(f"[*] Filename: {filename}")
        print(f"[*] Text length: {len(extracted_text)} characters")
        # Prepare OCR data in the format expected by webhook service
        ocr_data = {
            'success': True,
            'results': [
                {
                    'text': extracted_text,
                    'confidence': 0.95,
                    'bbox': [0, 0, 100, 100]
                }
            ],
            'text_count': 1,
            'processing_details': {
                'confidence': 0.95,
                'processing_time': '0.5s'
            }
        }
        # Use proper webhook service if available, otherwise fallback to mock
        if webhook_service and webhook_service.is_configured():
            print("[*] Using proper webhook service to send to N8N...")
            # Send to N8N webhook using the proper service
            import asyncio
            try:
                # Create event loop for async webhook service
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                webhook_results = loop.run_until_complete(
                    webhook_service.send_ocr_result(ocr_data, filename)
                )
                loop.close()
                # Check webhook results
                n8n_success = any(result.get('success', False) for result in webhook_results)
                if n8n_success:
                    print("[OK] N8N webhook sent successfully")
                    n8n_result = {
                        'success': True,
                        'message': 'Prescription sent to N8N webhook successfully',
                        'webhook_results': webhook_results,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print("[ERROR] N8N webhook failed, using mock service")
                    n8n_result = mock_n8n_service.process_prescription_webhook({
                        'patient_id': patient_id,
                        'medication_name': medication_name,
                        'extracted_text': extracted_text,
                        'filename': filename
                    })
                    n8n_result['webhook_results'] = webhook_results
            except Exception as e:
                print(f"[ERROR] Webhook service error: {e}, using mock service")
                n8n_result = mock_n8n_service.process_prescription_webhook({
                    'patient_id': patient_id,
                    'medication_name': medication_name,
                    'extracted_text': extracted_text,
                    'filename': filename
                })
        else:
            print("[*] Using mock N8N service (webhook service not configured)")
            n8n_result = mock_n8n_service.process_prescription_webhook({
                'patient_id': patient_id,
                'medication_name': medication_name,
                'extracted_text': extracted_text,
                'filename': filename
            })
        return jsonify(n8n_result), 200
    except Exception as e:
        print(f"[ERROR] Error in process_with_mock_n8n: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def process_with_n8n_webhook_service(data, webhook_service):
    """Process prescription with N8N webhook - EXACT from line 5371"""
    try:
        print("[*] Processing prescription with N8N webhook using medication folder service...")
        if not webhook_service or not webhook_service.is_configured():
            return jsonify({
                'success': False,
                'message': 'Webhook service not available or not configured'
            }), 503
        patient_id = data.get('patient_id')
        medication_name = data.get('medication_name')
        extracted_text = data.get('extracted_text')
        filename = data.get('filename')
        if not patient_id or not extracted_text:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        print(f"[*] Processing for patient: {patient_id}")
        print(f"[*] Medication: {medication_name}")
        print(f"[*] Filename: {filename}")
        print(f"[*] Text length: {len(extracted_text)} characters")
        # Prepare OCR data in the format expected by webhook service
        ocr_data = {
            'success': True,
            'results': [
                {
                    'text': extracted_text,
                    'confidence': 0.95,
                    'bbox': [0, 0, 100, 100]
                }
            ],
            'text_count': 1,
            'processing_details': {
                'confidence': 0.95,
                'processing_time': '0.5s'
            }
        }
        # Send to N8N webhook using the medication folder's webhook service
        import asyncio
        try:
            # Create event loop for async webhook service
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            webhook_results = loop.run_until_complete(
                webhook_service.send_ocr_result(ocr_data, filename)
            )
            loop.close()
            # Check webhook results
            n8n_success = any(result.get('success', False) for result in webhook_results)
            if n8n_success:
                print("[OK] N8N webhook sent successfully using medication folder service")
                return jsonify({
                    'success': True,
                    'message': 'Prescription sent to N8N webhook successfully',
                    'webhook_results': webhook_results,
                    'ocr_data': ocr_data,
                    'webhook_data': {
                        'patient_id': patient_id,
                        'medication_name': medication_name,
                        'filename': filename,
                        'extracted_text': extracted_text,
                        'timestamp': datetime.now().isoformat()
                    },
                    'timestamp': datetime.now().isoformat()
                }), 200
            else:
                print("[ERROR] N8N webhook failed")
                return jsonify({
                    'success': False,
                    'message': 'Failed to send to N8N webhook',
                    'webhook_results': webhook_results,
                    'error': 'All webhook attempts failed'
                }), 500
        except Exception as e:
            print(f"[ERROR] Error sending to N8N webhook: {e}")
            return jsonify({
                'success': False,
                'message': f'Error sending to N8N webhook: {str(e)}'
            }), 500
    except Exception as e:
        print(f"[ERROR] Error processing with N8N webhook: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def test_n8n_webhook_service(DEFAULT_WEBHOOK_URL):
    """Test N8N webhook directly - EXACT from line 5316"""
    try:
        print("[*] Testing N8N webhook...")
        # Test data
        test_data = {
            'success': True,
            'patient_id': 'TEST123',
            'medication_name': 'Test Medication',
            'filename': 'test_document.pdf',
            'extracted_text': 'This is a test prescription document for N8N webhook testing.',
            'full_content': 'This is a test prescription document for N8N webhook testing.',
            'file_type': 'application/pdf',
            'total_pages': 1,
            'processing_method': 'test',
            'timestamp': datetime.now().isoformat(),
            'results': [{'text': 'Test text', 'confidence': 0.95}]
        }
        n8n_url = DEFAULT_WEBHOOK_URL
        import requests
        response = requests.post(
            n8n_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        if response.status_code == 200:
            print("[OK] N8N webhook test successful!")
            return jsonify({
                'success': True,
                'message': 'N8N webhook test successful',
                'response_status': response.status_code,
                'response_text': response.text
            }), 200
        else:
            print(f"[ERROR] N8N webhook test failed: {response.status_code}")
            return jsonify({
                'success': False,
                'message': f'N8N webhook test failed: {response.status_code}',
                'response_status': response.status_code,
                'response_text': response.text
            }), 400
    except Exception as e:
        print(f"[ERROR] N8N webhook test error: {e}")
        return jsonify({
            'success': False,
            'message': f'N8N webhook test error: {str(e)}'
        }), 500
def test_medication_status_service(PADDLE_OCR_AVAILABLE, OCR_SERVICES_AVAILABLE,
                            enhanced_ocr_service, ocr_service, webhook_service, webhook_config_service):
    """Test medication service status - EXACT from line 5821"""
    try:
        status = {
            'paddle_ocr_available': PADDLE_OCR_AVAILABLE,
            'ocr_services_available': OCR_SERVICES_AVAILABLE,
            'enhanced_ocr_service': enhanced_ocr_service is not None,
            'ocr_service': ocr_service is not None,
            'webhook_service': webhook_service is not None,
            'webhook_config_service': webhook_config_service is not None,
            'timestamp': datetime.now().isoformat()
        }
        # Check webhook configurations
        if webhook_config_service:
            try:
                configs = webhook_config_service.get_all_configs()
                status['webhook_configs_count'] = len(configs)
                status['webhook_configs'] = [
                    {
                        'name': config.name,
                        'url': config.url,
                        'enabled': config.enabled
                    } for config in configs
                ]
            except Exception as e:
                status['webhook_configs_error'] = str(e)
        return jsonify({
            'success': True,
            'message': 'Medication service status check',
            'status': status
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error checking status: {str(e)}'
        }), 500
def test_file_upload_service(file, patient_id, medication_name):
    """Test file upload functionality - EXACT from line 5862"""
    try:
        print("[*] Testing file upload endpoint...")
        if not file or file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected',
                'test_type': 'file_upload_test'
            }), 400
        print(f"[OK] File upload test successful!")
        print(f"[*] File: {file.filename}")
        print(f"[*] Patient ID: {patient_id}")
        print(f"[*] Medication: {medication_name}")
        print(f"[*] File size: {len(file.read())} bytes")
        return jsonify({
            'success': True,
            'message': 'File upload test successful',
            'test_type': 'file_upload_test',
            'filename': file.filename,
            'patient_id': patient_id,
            'medication_name': medication_name,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        print(f"[ERROR] File upload test error: {e}")
        return jsonify({
            'success': False,
            'message': f'File upload test failed: {str(e)}',
            'test_type': 'file_upload_test',
            'error': str(e)
        }), 500
def save_tablet_tracking_daily_service(data):
    """Save tablet tracking data - EXACT from line 6272"""
    try:
        print(f"[*] Saving tablet tracking in medication_daily_tracking array: {data}")
        # Validate required fields
        required_fields = ['patient_id', 'tablet_name', 'tablet_taken_today']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        patient_id = data['patient_id']
        tablet_name = data['tablet_name']
        tablet_taken_today = data['tablet_taken_today']
        is_prescribed = data.get('is_prescribed', False)
        notes = data.get('notes', '')
        date_taken = data.get('date_taken', '')
        time_taken = data.get('time_taken', '')
        tracking_type = data.get('type', 'daily_tracking')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Create tablet tracking entry for medication_daily_tracking array
        tablet_entry = {
            'tablet_name': tablet_name,
            'tablet_taken_today': tablet_taken_today,
            'is_prescribed': is_prescribed,
            'notes': notes,
            'date_taken': date_taken,
            'time_taken': time_taken,
            'type': tracking_type,
            'timestamp': timestamp
        }
        # Add to patient's medication_daily_tracking array
        if 'medication_daily_tracking' not in patient:
            patient['medication_daily_tracking'] = []
        patient['medication_daily_tracking'].append(tablet_entry)
        # Update patient document
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"medication_daily_tracking": patient['medication_daily_tracking']}}
        )
        if result.modified_count > 0:
            print(f"[OK] Tablet tracking saved successfully in medication_daily_tracking array for patient: {patient_id}")
            return jsonify({
                'success': True,
                'message': f'Tablet "{tablet_name}" tracking saved successfully in medication_daily_tracking array',
                'tablet_entry': tablet_entry,
                'total_entries': len(patient['medication_daily_tracking'])
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save tablet tracking'}), 500
    except Exception as e:
        print(f"Error saving tablet tracking in medication_daily_tracking array: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def get_tablet_tracking_history_daily_service(patient_id):
    """Get tablet tracking history - EXACT from line 6339"""
    try:
        print(f"[*] Getting tablet tracking history from medication_daily_tracking array for patient: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        # Get medication_daily_tracking array
        tracking_history = patient.get('medication_daily_tracking', [])
        print(f"[OK] Retrieved {len(tracking_history)} tablet tracking entries from medication_daily_tracking array")
        return jsonify({
            'success': True,
            'message': f'Retrieved tablet tracking history from medication_daily_tracking array',
            'patient_id': patient_id,
            'tracking_history': tracking_history,
            'total_entries': len(tracking_history),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        print(f"Error getting tablet tracking history from medication_daily_tracking array: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def send_medication_reminders_manual_service(check_and_send_function):
    """Manually trigger medication reminder check - EXACT from line 6369"""
    try:
        print("[*] Manual medication reminder trigger requested")
        # Check and send medication reminders
        reminders_sent = check_and_send_function()
        return jsonify({
            'success': True,
            'message': f'Medication reminder check completed. {reminders_sent} reminders sent.',
            'reminders_sent': reminders_sent,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        print(f"Error sending medication reminders: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
def test_medication_reminder_email_service(patient_id, send_reminder_email_function):
    """Test medication reminder email - EXACT from line 6389"""
    try:
        print(f"[*] Testing medication reminder for patient ID: {patient_id}")
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        email = patient.get('email')
        username = patient.get('username')
        if not email or not username:
            return jsonify({'success': False, 'message': 'Patient email or username not found'}), 400
        # Send a test reminder email
        if send_reminder_email_function(
            email=email,
            username=username,
            medication_name="Test Medication",
            dosage="Test Dose",
            time="Test Time",
            frequency="Test Frequency",
            special_instructions="This is a test reminder email"
        ):
            return jsonify({
                'success': True,
                'message': f'Test medication reminder sent successfully to {email}',
                'patient_email': email,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to send test reminder email'}), 500
    except Exception as e:
        print(f"Error testing medication reminder: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500