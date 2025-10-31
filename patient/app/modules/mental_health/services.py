"""
Mental Health Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 5989-8398
Business logic for mental health tracking, assessments, AI chat, story generation

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
import uuid
from app.core.database import db
from app.shared.external_services.mental_health_service import mental_health_service


def submit_mood_checkin_service(data):
    """Submit a mood check-in for a patient - EXACT from line 5989"""
    try:
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract required fields
        patient_id = data.get('patient_id')
        mood = data.get('mood')
        note = data.get('note', '')
        date_str = data.get('date')
        
        if not patient_id or not mood:
            return jsonify({
                'success': False,
                'message': 'Patient ID and mood are required'
            }), 400
        
        # Parse date (use current date if not provided)
        if date_str:
            try:
                checkin_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use DD/MM/YYYY'
                }), 400
        else:
            checkin_date = datetime.now().date()
        
        # Check if database is connected
        if not db.is_connected():
            return jsonify({
                'success': False,
                'message': 'Database not connected'
            }), 503
        
        # Check if patient exists
        if db.patients_collection is None:
            return jsonify({
                'success': False,
                'message': 'Database connection error'
            }), 500
        
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404
        
        # Check if already checked in for this date (mood check-in only)
        existing_mood_checkin = db.mental_health_collection.find_one({
            "patient_id": patient_id,
            "date": checkin_date.isoformat(),
            "type": "mood_checkin"
        })
        
        if existing_mood_checkin:
            return jsonify({
                'success': False,
                'message': 'Already checked in for this date'
            }), 409
        
        # Create mood check-in entry
        mood_entry = {
            "patient_id": patient_id,
            "mood": mood,
            "note": note,
            "date": checkin_date.isoformat(),
            "timestamp": datetime.now().isoformat(),
            "type": "mood_checkin",
            "created_at": datetime.now().isoformat()
        }
        
        # Insert into mental health collection
        result = db.mental_health_collection.insert_one(mood_entry)
        
        if result.inserted_id:
            print(f"[OK] Mood check-in saved for patient {patient_id}: {mood}")
            
            # Update patient's mental health logs count
            db.patients_collection.update_one(
                {"patient_id": patient_id},
                {
                    "$push": {"mental_health_logs": mood_entry},
                    "$inc": {"mental_health_logs_count": 1}
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Mood check-in saved successfully',
                'data': {
                    'id': str(result.inserted_id),
                    'patient_id': patient_id,
                    'mood': mood,
                    'date': checkin_date.isoformat(),
                    'timestamp': mood_entry['timestamp']
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save mood check-in'
            }), 500
            
    except Exception as e:
        print(f"[ERROR] Mood check-in error: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500


def get_mental_health_history_service(patient_id):
    """Get mental health history for a patient - EXACT from line 6109"""
    try:
        # Check if database is connected
        if not db.is_connected():
            return jsonify({
                'success': False,
                'message': 'Database not connected'
            }), 503
        
        if db.mental_health_collection is None:
            return jsonify({
                'success': False,
                'message': 'Database connection error'
            }), 500
        
        # Get mood check-ins for the patient
        mood_entries = list(db.mental_health_collection.find(
            {"patient_id": patient_id, "type": "mood_checkin"},
            {"_id": 0}  # Exclude MongoDB _id
        ).sort("date", -1).limit(30))  # Last 30 entries
        
        # Get assessment entries for the patient
        assessment_entries = list(db.mental_health_collection.find(
            {"patient_id": patient_id, "type": "mental_health_assessment"},
            {"_id": 0}  # Exclude MongoDB _id
        ).sort("date", -1).limit(30))  # Last 30 entries
        
        return jsonify({
            'success': True,
            'data': {
                'patient_id': patient_id,
                'mood_history': mood_entries,
                'assessment_history': assessment_entries,
                'total_mood_entries': len(mood_entries),
                'total_assessment_entries': len(assessment_entries)
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get mental health history error: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500


def submit_mental_health_assessment_service(data):
    """Submit a mental health assessment for a patient - EXACT from line 6156"""
    try:
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract required fields
        patient_id = data.get('patient_id')
        score = data.get('score')
        date_str = data.get('date')
        
        if not patient_id or score is None:
            return jsonify({
                'success': False,
                'message': 'Patient ID and score are required'
            }), 400
        
        # Validate score range
        if not isinstance(score, (int, float)) or score < 1 or score > 10:
            return jsonify({
                'success': False,
                'message': 'Score must be a number between 1 and 10'
            }), 400
        
        # Parse date (use current date if not provided)
        if date_str:
            try:
                assessment_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use DD/MM/YYYY'
                }), 400
        else:
            assessment_date = datetime.now().date()
        
        # Check if database is connected
        if not db.is_connected():
            return jsonify({
                'success': False,
                'message': 'Database not connected'
            }), 503
        
        # Check if patient exists
        if db.patients_collection is None:
            return jsonify({
                'success': False,
                'message': 'Database connection error'
            }), 500
        
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404
        
        # Create assessment entry
        assessment_entry = {
            "patient_id": patient_id,
            "score": float(score),
            "date": assessment_date.isoformat(),
            "timestamp": datetime.now().isoformat(),
            "type": "mental_health_assessment",
            "questions": data.get('questions', []),
            "answers": data.get('answers', []),
            "notes": data.get('notes', ''),
            "created_at": datetime.now().isoformat()
        }
        
        # Insert into mental health collection
        result = db.mental_health_collection.insert_one(assessment_entry)
        
        if result.inserted_id:
            print(f"[OK] Mental health assessment saved for patient {patient_id}: score {score}")
            
            # Update patient's mental health logs
            db.patients_collection.update_one(
                {"patient_id": patient_id},
                {
                    "$push": {"mental_health_logs": assessment_entry},
                    "$inc": {"mental_health_assessments_count": 1}
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Mental health assessment saved successfully',
                'data': {
                    'id': str(result.inserted_id),
                    'patient_id': patient_id,
                    'score': score,
                    'date': assessment_date.isoformat(),
                    'timestamp': assessment_entry['timestamp']
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save mental health assessment'
            }), 500
            
    except Exception as e:
        print(f"[ERROR] Mental health assessment error: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500


def generate_mental_health_story_service(data):
    """Generate a mental health assessment story - EXACT from line 8052"""
    try:
        story_type = data.get('story_type', 'pregnancy')
        scenario = data.get('scenario', 'pregnancy_mental_health')
        
        result = mental_health_service.generate_story(story_type, scenario)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating story: {str(e)}'
        }), 500


def assess_mental_health_service(data, patient_id):
    """Assess mental health based on story responses - EXACT from line 8069"""
    try:
        answers = data.get('answers', [])
        story_id = data.get('story_id', '')
        
        if not answers:
            return jsonify({
                'success': False,
                'error': 'Answers are required'
            }), 400
        
        result = mental_health_service.assess_mental_health(answers, story_id, patient_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error assessing mental health: {str(e)}'
        }), 500


def generate_mental_health_audio_service(data):
    """Generate Tamil audio for mental health story - EXACT from line 8093"""
    try:
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text is required for audio generation'
            }), 400
        
        result = mental_health_service.generate_audio(text)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating audio: {str(e)}'
        }), 500


def get_mental_health_story_types_service():
    """Get available mental health story types - EXACT from line 8115"""
    try:
        story_types = {
            "pregnancy": "Stories about pregnancy-related mental health challenges",
            "postpartum": "Stories about postpartum mental health experiences", 
            "general": "General mental health and life challenges"
        }
        
        return jsonify({
            'success': True,
            'story_types': story_types
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting story types: {str(e)}'
        }), 500


def mental_health_service_health_service():
    """Check mental health service health - EXACT from line 8135"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'Mental Health Assessment',
            'features': [
                'Story generation',
                'Mental health assessment',
                'Tamil audio generation',
                'AI-powered analysis'
            ],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking service health: {str(e)}'
        }), 500


def mental_health_chat_service(data, patient_id):
    """Send a message to the mental health AI chat - EXACT from line 8159"""
    try:
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Message is required'
            }), 400

        message = data['message']
        context = data.get('context')
        mood = data.get('mood')
        session_id = data.get('session_id')
        user_profile = data.get('user_profile', {})

        # Generate AI response using the mental health service
        result = mental_health_service.generate_chat_response(
            message=message,
            patient_id=patient_id,
            context=context,
            mood=mood,
            session_id=session_id,
            user_profile=user_profile
        )

        return jsonify(result), 200

    except Exception as e:
        print(f"[ERROR] Mental health chat error: {e}")
        return jsonify({
            'success': False,
            'message': f'Chat error: {str(e)}'
        }), 500


def get_mental_health_chat_history_service(patient_id, limit=50, offset=0):
    """Get mental health chat history for a patient - EXACT from line 8197"""
    try:
        # Get chat sessions from database
        if db.mental_health_collection is None:
            return jsonify({
                'success': False,
                'message': 'Database not available'
            }), 500

        # Query chat sessions
        chat_sessions = list(db.mental_health_collection.find(
            {"patient_id": patient_id, "type": "chat_session"}
        ).sort("created_at", -1).skip(offset).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for session in chat_sessions:
            session["_id"] = str(session["_id"])
            if isinstance(session.get("created_at"), datetime):
                session["created_at"] = session["created_at"].isoformat()
            if isinstance(session.get("last_activity"), datetime):
                session["last_activity"] = session["last_activity"].isoformat()

        return jsonify({
            'success': True,
            'sessions': chat_sessions,
            'count': len(chat_sessions)
        }), 200

    except Exception as e:
        print(f"[ERROR] Get mental health chat history error: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get chat history: {str(e)}'
        }), 500


def start_mental_health_chat_session_service(data, patient_id):
    """Start a new mental health chat session - EXACT from line 8239"""
    try:
        initial_mood = data.get('initial_mood')
        user_profile = data.get('user_profile', {})

        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "patient_id": patient_id,
            "type": "chat_session",
            "initial_mood": initial_mood,
            "user_profile": user_profile,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "messages": [],
            "current_mood": initial_mood,
            "session_data": {}
        }

        # Save session to database
        if db.mental_health_collection is not None:
            db.mental_health_collection.insert_one(session_data)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Chat session started successfully'
        }), 200

    except Exception as e:
        print(f"[ERROR] Start mental health chat session error: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to start chat session: {str(e)}'
        }), 500


def end_mental_health_chat_session_service(session_id, data, patient_id):
    """End a mental health chat session - EXACT from line 8280"""
    try:
        summary = data.get('summary')

        # Update session in database
        if db.mental_health_collection is not None:
            update_data = {
                "last_activity": datetime.now(),
                "ended_at": datetime.now(),
                "status": "ended"
            }
            if summary:
                update_data["summary"] = summary

            db.mental_health_collection.update_one(
                {"session_id": session_id, "patient_id": patient_id, "type": "chat_session"},
                {"$set": update_data}
            )

        return jsonify({
            'success': True,
            'message': 'Chat session ended successfully'
        }), 200

    except Exception as e:
        print(f"[ERROR] End mental health chat session error: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to end chat session: {str(e)}'
        }), 500


def get_mental_health_assessments_service(patient_id, limit=10, offset=0):
    """Get mental health assessments for a patient - EXACT from line 8316"""
    try:
        # Get assessments from database using mental health service
        if mental_health_service.mental_health_collection is not None:
            assessments = list(mental_health_service.mental_health_collection.find(
                {"patient_id": patient_id, "type": "mental_health_assessment"}
            ).sort("created_at", -1).skip(offset).limit(limit))

            # Convert ObjectId to string for JSON serialization
            for assessment in assessments:
                assessment["_id"] = str(assessment["_id"])
                if isinstance(assessment.get("created_at"), datetime):
                    assessment["created_at"] = assessment["created_at"].isoformat()

            return jsonify({
                'success': True,
                'assessments': assessments,
                'count': len(assessments)
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Database not available'
            }), 500

    except Exception as e:
        print(f"[ERROR] Get mental health assessments error: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get assessments: {str(e)}'
        }), 500


def debug_mental_health_database_service(patient_id):
    """Debug endpoint to check mental health database status - EXACT from line 8355"""
    try:
        debug_info = {
            'patient_id': patient_id,
            'database_connected': mental_health_service.mental_health_collection is not None,
            'database_name': mental_health_service.db.name if mental_health_service.db else None,
            'collection_name': mental_health_service.mental_health_collection.name if mental_health_service.mental_health_collection else None,
        }
        
        if mental_health_service.mental_health_collection is not None:
            # Get total count
            total_count = mental_health_service.mental_health_collection.count_documents({})
            patient_count = mental_health_service.mental_health_collection.count_documents({"patient_id": patient_id})
            
            debug_info.update({
                'total_assessments': total_count,
                'patient_assessments': patient_count,
                'recent_assessments': list(mental_health_service.mental_health_collection.find(
                    {"patient_id": patient_id}
                ).sort("created_at", -1).limit(3))
            })
            
            # Convert ObjectId to string for JSON serialization
            for assessment in debug_info.get('recent_assessments', []):
                assessment["_id"] = str(assessment["_id"])
                if isinstance(assessment.get("created_at"), datetime):
                    assessment["created_at"] = assessment["created_at"].isoformat()
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        }), 200

    except Exception as e:
        print(f"[ERROR] Debug mental health database error: {e}")
        return jsonify({
            'success': False,
            'message': f'Debug failed: {str(e)}'
        }), 500
