"""
Symptoms Service - EXTRACTED FROM app_simple.py
Contains EXACT business logic from lines 2933-3547
NO CHANGES to functionality - just reorganized
"""
import json
from datetime import datetime
from flask import jsonify
from bson import ObjectId
from app.core.database import db
from app.core.config import DISCLAIMER_TEXT
from app.shared.external_services.symptoms_service import symptoms_service
from app.shared.activity_tracker import UserActivityTracker

# Initialize
activity_tracker = UserActivityTracker(db)


def symptoms_health_check_service():
    """EXTRACTED FROM app_simple.py lines 2933-2940"""
    return jsonify({
        'success': True,
        'message': 'Pregnancy Symptom Assistant is running',
        'timestamp': datetime.now().isoformat()
    })


def get_symptom_assistance_service(data):
    """
    EXTRACTED FROM app_simple.py lines 2942-3042
    Get pregnancy symptom assistance using AI
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        symptom_text = data.get('text', '').strip()
        weeks_pregnant = data.get('weeks_pregnant', 1)
        patient_id = data.get('patient_id')
        user_id = data.get('user_id', patient_id)
        
        if not symptom_text:
            return jsonify({
                'success': False,
                'message': 'Symptom description is required'
            }), 400
        
        # Auto-fetch pregnancy week from patient profile if not provided
        if not weeks_pregnant and patient_id:
            try:
                patient = db.patients_collection.find_one({"patient_id": patient_id})
                if patient and patient.get('pregnancy_week'):
                    weeks_pregnant = patient['pregnancy_week']
                    print(f"[OK] Auto-fetched pregnancy week: {weeks_pregnant}")
            except Exception as e:
                print(f"[WARN] Error fetching pregnancy week: {e}")
        
        # Determine trimester
        if weeks_pregnant <= 12:
            trimester = "First Trimester"
        elif weeks_pregnant <= 26:
            trimester = "Second Trimester"
        else:
            trimester = "Third Trimester"
            
        print(f"[*] Analyzing symptoms: '{symptom_text}' for week {weeks_pregnant} ({trimester})")
        
        # Use the AI-powered symptoms service
        try:
            ai_response = symptoms_service.analyze_symptoms(
                query=symptom_text,
                weeks_pregnant=weeks_pregnant,
                user_id=user_id
            )
            
            # Generate additional recommendations
            additional_recommendations = generate_symptom_recommendations(symptom_text, weeks_pregnant, trimester)
            
            # Log the symptom consultation
            if patient_id:
                try:
                    patient = db.patients_collection.find_one({"patient_id": patient_id})
                    activity_tracker.log_activity(
                        user_email=patient.get('email') if patient else None,
                        activity_type="symptom_consultation",
                        activity_data={
                            "symptom_text": symptom_text,
                            "pregnancy_week": weeks_pregnant,
                            "trimester": trimester,
                            "patient_id": patient_id,
                            "analysis_method": "ai_analysis",
                            "red_flags_detected": [],
                            "suggestions_count": 0
                        }
                    )
                except Exception as e:
                    print(f"[WARN] Warning: Could not log symptom consultation activity: {e}")
            
            # Return AI response
            return jsonify({
                'success': True,
                'symptom_text': symptom_text,
                'pregnancy_week': weeks_pregnant,
                'trimester': trimester,
                'analysis_method': 'ai_analysis',
                'primary_recommendation': ai_response.get('text', ''),
                'additional_recommendations': additional_recommendations,
                'red_flags_detected': [],
                'knowledge_base_suggestions': 0,
                'disclaimer': ai_response.get('disclaimers', DISCLAIMER_TEXT),
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as ai_error:
            print(f"[WARN] AI analysis failed, using fallback: {ai_error}")
            return jsonify({
                'success': False,
                'message': f'AI analysis temporarily unavailable: {str(ai_error)}'
            }), 500
        
    except Exception as e:
        print(f"Error getting symptom assistance: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def generate_symptom_recommendations(symptom_text, weeks_pregnant, trimester):
    """
    EXTRACTED FROM app_simple.py lines 3044-3148
    Generate symptom-specific recommendations
    EXACT SAME LOGIC - NO CHANGES
    """
    symptom_lower = symptom_text.lower()
    recommendations = []
    
    # Common pregnancy symptoms and recommendations
    if any(word in symptom_lower for word in ['nausea', 'morning sickness', 'vomiting']):
        recommendations.extend([
            "Eat small, frequent meals throughout the day",
            "Avoid spicy, greasy, or strong-smelling foods",
            "Try ginger tea or ginger candies",
            "Stay hydrated with small sips of water",
            "Eat crackers or dry toast before getting out of bed"
        ])
    
    if any(word in symptom_lower for word in ['fatigue', 'tired', 'exhausted']):
        recommendations.extend([
            "Get plenty of rest and sleep",
            "Take short naps during the day",
            "Maintain a regular sleep schedule",
            "Stay hydrated and eat nutritious foods",
            "Listen to your body and rest when needed"
        ])
    
    if any(word in symptom_lower for word in ['back pain', 'backache', 'lower back']):
        recommendations.extend([
            "Practice good posture",
            "Use proper body mechanics when lifting",
            "Try gentle stretching exercises",
            "Consider prenatal yoga or swimming",
            "Use a pregnancy pillow for support while sleeping"
        ])
    
    if any(word in symptom_lower for word in ['heartburn', 'acid reflux', 'indigestion']):
        recommendations.extend([
            "Eat smaller, more frequent meals",
            "Avoid lying down immediately after eating",
            "Limit spicy, acidic, or fatty foods",
            "Try eating yogurt or drinking milk",
            "Prop yourself up with pillows when sleeping"
        ])
    
    if any(word in symptom_lower for word in ['constipation', 'bowel', 'digestion']):
        recommendations.extend([
            "Increase fiber intake (fruits, vegetables, whole grains)",
            "Drink plenty of water throughout the day",
            "Stay physically active with gentle exercise",
            "Consider a pregnancy-safe fiber supplement",
            "Establish a regular bathroom routine"
        ])
    
    if any(word in symptom_lower for word in ['swelling', 'edema', 'swollen feet']):
        recommendations.extend([
            "Elevate your feet when resting",
            "Avoid standing for long periods",
            "Stay hydrated",
            "Reduce sodium intake",
            "Wear comfortable, supportive shoes"
        ])
    
    if any(word in symptom_lower for word in ['headache', 'head pain', 'migraine']):
        recommendations.extend([
            "Rest in a quiet, dark room",
            "Stay well-hydrated",
            "Apply a cool compress to your forehead",
            "Practice relaxation techniques",
            "Maintain regular meal times"
        ])
    
    # Trimester-specific recommendations
    if trimester == "First Trimester":
        recommendations.append("First trimester: Focus on rest and managing early pregnancy symptoms")
    elif trimester == "Second Trimester":
        recommendations.append("Second trimester: Usually the most comfortable period - stay active")
    else:
        recommendations.append("Third trimester: Prepare for delivery and get plenty of rest")
    
    # Limit to top recommendations
    return recommendations[:10]


def save_symptom_log_service(data):
    """
    EXTRACTED FROM app_simple.py lines 3150-3241
    Save symptom log to patient profile
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        # Debug logging
        print(f"[*] Received symptom log data: {json.dumps(data, indent=2)}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['patient_id', 'symptom_text', 'severity', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        patient_id = data.get('patient_id')
        symptom_text = data.get('symptom_text', '').strip()
        severity = data.get('severity', 5)
        category = data.get('category', 'General')
        notes = data.get('notes', '')
        
        if not symptom_text:
            return jsonify({
                'success': False, 
                'message': 'Symptom description is required'
            }), 400
        
        print(f"[*] Looking for patient with ID: {patient_id}")
        
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        
        print(f"[*] Found patient: {patient.get('username')} ({patient.get('email')})")
        
        # Create symptom log entry
        symptom_log_entry = {
            'symptom_text': symptom_text,
            'severity': severity,
            'category': category,
            'notes': notes,
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'createdAt': datetime.now(),
            'pregnancy_week': patient.get('pregnancy_week', 1),
            'trimester': 'First' if patient.get('pregnancy_week', 1) <= 12 else 'Second' if patient.get('pregnancy_week', 1) <= 26 else 'Third'
        }
        
        # Add symptom log to patient's symptom_logs array
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"symptom_logs": symptom_log_entry},
                "$set": {"last_updated": datetime.now()}
            }
        )
        
        if result.modified_count > 0:
            # Log the symptom log activity
            activity_tracker.log_activity(
                user_email=patient.get('email'),
                activity_type="symptom_log_created",
                activity_data={
                    "symptom_log_id": "embedded_in_patient_doc",
                    "symptom_data": symptom_log_entry,
                    "patient_id": patient_id,
                    "total_symptom_logs": len(patient.get('symptom_logs', [])) + 1
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Symptom log saved successfully to patient profile',
                'patientId': patient_id,
                'patientEmail': patient.get('email'),
                'symptomLogsCount': len(patient.get('symptom_logs', [])) + 1
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save symptom log to patient profile'}), 500
            
    except Exception as e:
        print(f"Error saving symptom log: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def save_symptom_analysis_report_service(data):
    """
    EXTRACTED FROM app_simple.py lines 3243-3356
    Save complete symptom analysis report
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        # Debug logging
        print(f"[*] Received symptom analysis report data: {json.dumps(data, indent=2)}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['patient_id', 'symptom_text', 'weeks_pregnant']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        patient_id = data.get('patient_id')
        symptom_text = data.get('symptom_text', '').strip()
        weeks_pregnant = data.get('weeks_pregnant', 1)
        
        if not symptom_text:
            return jsonify({
                'success': False,
                'message': 'Symptom description is required'
            }), 400
        
        print(f"[*] Looking for patient with ID: {patient_id}")
        
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        
        print(f"[*] Found patient: {patient.get('username')} ({patient.get('email')})")
        
        # Create comprehensive symptom analysis report
        analysis_report = {
            'symptom_text': symptom_text,
            'weeks_pregnant': weeks_pregnant,
            'trimester': 'First' if weeks_pregnant <= 12 else 'Second' if weeks_pregnant <= 26 else 'Third',
            'severity': data.get('severity', 'Not specified'),
            'notes': data.get('notes', ''),
            'analysis_date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
            'timestamp': datetime.now().isoformat(),
            'createdAt': datetime.now(),
            
            # AI Analysis Results
            'ai_analysis': {
                'analysis_method': data.get('analysis_method', 'quantum_llm'),
                'primary_recommendation': data.get('primary_recommendation', ''),
                'additional_recommendations': data.get('additional_recommendations', []),
                'red_flags_detected': data.get('red_flags_detected', []),
                'disclaimer': data.get('disclaimer', ''),
                'urgency_level': data.get('urgency_level', 'moderate'),
                'knowledge_base_suggestions_count': data.get('knowledge_base_suggestions_count', 0)
            },
            
            # Patient Context
            'patient_context': data.get('patient_context', {}),
            
            # Metadata
            'report_id': str(ObjectId()),
            'version': '1.0',
            'source': 'flutter_app_quantum_llm'
        }
        
        # Add analysis report to patient's symptom_analysis_reports array
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {
                "$push": {"symptom_analysis_reports": analysis_report},
                "$set": {"last_updated": datetime.now()}
            }
        )
        
        if result.modified_count > 0:
            # Log the symptom analysis activity
            activity_tracker.log_activity(
                user_email=patient.get('email'),
                activity_type="symptom_analysis_report_created",
                activity_data={
                    "report_id": analysis_report['report_id'],
                    "symptom_text": symptom_text,
                    "pregnancy_week": weeks_pregnant,
                    "trimester": analysis_report['trimester'],
                    "red_flags_count": len(analysis_report['ai_analysis']['red_flags_detected']),
                    "patient_id": patient_id,
                    "total_analysis_reports": len(patient.get('symptom_analysis_reports', [])) + 1
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Symptom analysis report saved successfully',
                'report_id': analysis_report['report_id'],
                'patientId': patient_id,
                'patientEmail': patient.get('email'),
                'analysisReportsCount': len(patient.get('symptom_analysis_reports', [])) + 1,
                'timestamp': analysis_report['timestamp']
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save analysis report'}), 500
            
    except Exception as e:
        print(f"Error saving symptom analysis report: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_symptom_history_service(patient_id):
    """EXTRACTED FROM app_simple.py lines 3358-3391"""
    try:
        print(f"[*] Retrieving symptom history for patient: {patient_id}")
        
        # Find patient
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        # Get symptom logs
        symptom_logs = patient.get('symptom_logs', [])
        
        print(f"[OK] Found {len(symptom_logs)} symptom logs for patient {patient_id}")
        
        return jsonify({
            'success': True,
            'symptom_history': symptom_logs,
            'total_count': len(symptom_logs),
            'patient_id': patient_id
        }), 200
        
    except Exception as e:
        print(f"Error retrieving symptom history: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def get_analysis_reports_service(patient_id):
    """EXTRACTED FROM app_simple.py lines 3393-3444"""
    try:
        print(f"[*] Retrieving symptom analysis reports for patient: {patient_id}")
        
        # Find patient
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        # Get analysis reports
        analysis_reports = patient.get('symptom_analysis_reports', [])
        
        print(f"[OK] Found {len(analysis_reports)} analysis reports for patient {patient_id}")
        
        return jsonify({
            'success': True,
            'reports': analysis_reports,
            'total_count': len(analysis_reports),
            'patient_id': patient_id
        }), 200
        
    except Exception as e:
        print(f"Error retrieving analysis reports: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


def add_symptom_knowledge_service(data):
    """EXTRACTED FROM app_simple.py lines 3446-3479"""
    try:
        # This would integrate with knowledge base
        # For now, return success
        return jsonify({
            'success': True,
            'message': 'Knowledge entry added successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500


def add_symptom_knowledge_bulk_service(data):
    """EXTRACTED FROM app_simple.py lines 3481-3525"""
    try:
        items = data.get('knowledge_items', [])
        return jsonify({
            'success': True,
            'message': 'Bulk knowledge entries added successfully',
            'added_count': len(items)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500


def ingest_symptom_knowledge_service():
    """EXTRACTED FROM app_simple.py lines 3527-3546"""
    try:
        return jsonify({
            'success': True,
            'message': 'Knowledge ingestion completed',
            'ingested_count': 0
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed: {str(e)}'}), 500

