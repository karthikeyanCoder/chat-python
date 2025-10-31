"""
Nutrition Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 6566-7070
Business logic for nutrition tracking, GPT-4 food analysis, transcription

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
import requests
import json
import os
from app.core.database import db


def health_check_service():
    """Health check - EXACT from line 6566"""
    return jsonify({
        'success': True,
        'message': 'Nutrition service is running',
        'timestamp': datetime.now().isoformat(),
        'database_connected': db.patients_collection is not None
    })


def transcribe_audio_service(data):
    """Transcribe audio using N8N webhook - EXACT from line 6576"""
    try:
        print("[*] Transcription request received")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        audio_data = data.get('audio')
        if not audio_data:
            return jsonify({
                'success': False,
                'message': 'Audio data is required'
            }), 400
        
        use_n8n = data.get('use_n8n', True)  # Default to N8N
        method = data.get('method', 'n8n_webhook')  # Default to N8N webhook
        context = data.get('context', 'food_tracking')  # Default to food tracking
        
        # Determine which N8N webhook to use based on context
        if context == 'symptoms_tracking':
            webhook_url = 'https://n8n.srv795087.hstgr.cloud/webhook/symptoms'
            print(f"[*] Using symptoms N8N webhook for symptoms tracking")
        else:
            webhook_url = 'https://n8n.srv795087.hstgr.cloud/webhook/food'
            print(f"[*] Using food N8N webhook for food tracking")
            
        print(f"[*] Using method: {method}, use_n8n: {use_n8n}, context: {context}")
        if True:  # Always use N8N webhook
            try:
                print("[*] Trying N8N webhook for transcription + translation...")
                
                # Prepare payload for N8N - try multiple field formats
                n8n_payload = {
                    # Different possible field names for audio data
                    'audio_data': audio_data,
                    'audio': audio_data,
                    'file': audio_data,
                    'data': audio_data,
                    'input': audio_data,
                    'base64': audio_data,
                    
                    # Action and context
                    'action': 'transcribe_and_translate',
                    'type': 'audio_transcription',
                    'source_language': 'auto',
                    'target_language': 'en',
                    'audio_format': 'webm',
                    'context': context,
                    'format': 'base64',
                    'encoding': 'base64',
                }
                
                print(f"[*] Sending to N8N: {webhook_url}")
                print(f"[*] Payload keys: {list(n8n_payload.keys())}")
                print(f"[*] Audio data length: {len(audio_data) if audio_data else 0}")
                print(f"[*] Full payload: {json.dumps({k: v if k != 'audio_data' else f'[{len(v)} chars]' for k, v in n8n_payload.items()})}")
                
                n8n_response = requests.post(
                    webhook_url,
                    json=n8n_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=60
                )
                
                if n8n_response.status_code == 200:
                    n8n_data = n8n_response.json()
                    print(f"[*] N8N response data: {n8n_data}")
                    
                    # Handle different N8N response formats
                    transcription = None
                    
                    # Format 1: {output: "text"}
                    if 'output' in n8n_data:
                        transcription = str(n8n_data['output'])
                    
                    # Format 2: {success: true, transcription: "text"}
                    elif n8n_data.get('success') or n8n_data.get('status') == 'success':
                        transcription = n8n_data.get('transcription') or n8n_data.get('translated_text') or n8n_data.get('text')
                    
                    # Format 3: Direct text response
                    elif isinstance(n8n_data, str):
                        transcription = n8n_data
                    
                    if transcription:
                        print(f"[OK] N8N webhook transcription successful: {transcription[:50]}...")
                        return jsonify({
                            'success': True,
                            'transcription': transcription,
                            'output': transcription,  # Include for compatibility
                            'language': 'auto',
                            'method': 'n8n_webhook',
                            'original_text': n8n_data.get('original_text'),
                            'translation_note': 'Processed via N8N webhook',
                            'timestamp': datetime.now().isoformat()
                        }), 200
                
                print(f"[ERROR] N8N webhook failed: {n8n_response.status_code}")
                return jsonify({
                    'success': False,
                    'message': f'N8N webhook failed with status {n8n_response.status_code}',
                    'method': 'n8n_webhook'
                }), 500
            except Exception as e:
                print(f"[ERROR] N8N webhook error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'N8N webhook error: {str(e)}',
                    'method': 'n8n_webhook'
                }), 500
        
        # No Whisper fallback - N8N only
        return jsonify({
            'success': False,
            'message': 'N8N webhook is the only supported transcription method',
            'method': 'n8n_webhook'
        }), 400
            
    except Exception as e:
        print(f"[ERROR] Error in transcription: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def analyze_food_with_gpt4_service(data):
    """Analyze food using GPT-4 - EXACT from line 6706"""
    try:
        print("[*] GPT-4 analysis request received")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        food_input = data.get('food_input', '')
        pregnancy_week = data.get('pregnancy_week', 1)
        user_id = data.get('userId', '')
        
        if not food_input:
            return jsonify({
                'success': False,
                'message': 'Food input is required'
            }), 400
        
        # Get OpenAI API key
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'success': False,
                'message': 'OpenAI API key not configured'
            }), 500
        
        try:
            from openai import OpenAI
        except ImportError:
            return jsonify({
                'success': False,
                'message': 'OpenAI package not installed. Run: pip install openai'
            }), 500
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Create GPT-4 prompt
        prompt = f"""
        Analyze this food item for a pregnant woman at week {pregnancy_week}:
        
        Food: {food_input}
        
        Provide a detailed analysis in JSON format with the following structure:
        {{
            "nutritional_breakdown": {{
                "estimated_calories": <number>,
                "protein_grams": <number>,
                "carbohydrates_grams": <number>,
                "fat_grams": <number>,
                "fiber_grams": <number>
            }},
            "pregnancy_benefits": {{
                "nutrients_for_fetal_development": ["list of specific nutrients"],
                "benefits_for_mother": ["list of benefits"],
                "week_specific_advice": "specific advice for week {pregnancy_week}"
            }},
            "safety_considerations": {{
                "food_safety_tips": ["list of safety tips"],
                "cooking_recommendations": ["cooking guidelines"]
            }},
            "smart_recommendations": {{
                "next_meal_suggestions": ["suggestions for next meal"],
                "hydration_tips": "water intake advice"
            }}
        }}
        
        Focus on pregnancy-specific nutrition needs.
        """
        
        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutrition expert specializing in pregnancy nutrition. Provide accurate, detailed analysis in the exact JSON format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        # Extract response
        gpt_response = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            # Remove markdown formatting if present
            if gpt_response.startswith('```json'):
                gpt_response = gpt_response.replace('```json', '').replace('```', '').strip()
            
            analysis_data = json.loads(gpt_response)
            
            # Save to database if user_id provided
            if user_id:
                try:
                    # Find patient
                    patient = db.patients_collection.find_one({"patient_id": user_id})
                    if patient:
                        # Initialize food_data array if not exists
                        if 'food_data' not in patient:
                            patient['food_data'] = []
                        
                        # Add GPT-4 analysis to food_data
                        food_entry = {
                            'type': 'gpt4_analysis',
                            'food_input': food_input,
                            'analysis': analysis_data,
                            'pregnancy_week': pregnancy_week,
                            'timestamp': datetime.now().isoformat(),
                            'created_at': datetime.now()
                        }
                        
                        patient['food_data'].append(food_entry)
                        
                        # Update patient document
                        db.patients_collection.update_one(
                            {"patient_id": user_id},
                            {"$set": {"food_data": patient['food_data']}}
                        )
                        
                        print(f"[OK] GPT-4 analysis saved to database for user: {user_id}")
                    else:
                        print(f"[WARN] Patient not found for user ID: {user_id}")
                except Exception as e:
                    print(f"[WARN] Could not save to database: {e}")
            
            print(f"[OK] GPT-4 analysis successful for: {food_input[:50]}...")
            
            return jsonify({
                'success': True,
                'analysis': analysis_data,
                'food_input': food_input,
                'pregnancy_week': pregnancy_week,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parsing error: {e}")
            print(f"[WARN] Raw GPT response: {gpt_response[:200]}...")
            
            # Fallback analysis
            fallback_analysis = {
                "nutritional_breakdown": {
                    "estimated_calories": 0,
                    "protein_grams": 0,
                    "carbohydrates_grams": 0,
                    "fat_grams": 0,
                    "fiber_grams": 0
                },
                "pregnancy_benefits": {
                    "nutrients_for_fetal_development": ["General nutrients"],
                    "benefits_for_mother": ["General benefits"],
                    "week_specific_advice": f"Consult your doctor for week {pregnancy_week} specific advice"
                },
                "safety_considerations": {
                    "food_safety_tips": ["Ensure food is properly cooked", "Wash fruits and vegetables"],
                    "cooking_recommendations": ["Cook thoroughly", "Avoid raw foods"]
                },
                "smart_recommendations": {
                    "next_meal_suggestions": ["Balanced meal with protein and vegetables"],
                    "hydration_tips": "Drink plenty of water throughout the day"
                },
                "note": "Analysis generated with fallback due to parsing error"
            }
            
            return jsonify({
                'success': True,
                'analysis': fallback_analysis,
                'food_input': food_input,
                'pregnancy_week': pregnancy_week,
                'timestamp': datetime.now().isoformat(),
                'fallback_used': True
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Error in GPT-4 analysis: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def save_food_entry_service(data):
    """Save basic food entry to patient's food_data array - EXACT from line 6898"""
    try:
        print("[*] Food entry save request received")
        
        print(f"[*] Received food entry data: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        user_id = data.get('userId')
        # Accept both 'food_input' and 'food_details' for backward compatibility
        food_input = data.get('food_input') or data.get('food_details', '')
        pregnancy_week = data.get('pregnancy_week', 1)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        if not food_input:
            return jsonify({
                'success': False,
                'message': 'Food input is required'
            }), 400
        
        # Find patient
        patient = db.patients_collection.find_one({"patient_id": user_id})
        if not patient:
            return jsonify({
                'success': False,
                'message': f'Patient not found with ID: {user_id}'
            }), 404
        
        # Initialize food_data array if not exists
        if 'food_data' not in patient:
            patient['food_data'] = []
        
        # Create food entry with all available fields
        food_entry = {
            'type': 'basic_entry',
            'food_input': food_input,
            'food_details': food_input,  # Also store as food_details for consistency
            'pregnancy_week': pregnancy_week,
            'meal_type': data.get('meal_type', ''),
            'notes': data.get('notes', ''),
            'transcribed_text': data.get('transcribed_text', ''),
            'nutritional_breakdown': data.get('nutritional_breakdown', {}),
            'gpt4_analysis': data.get('gpt4_analysis', {}),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'created_at': datetime.now()
        }
        
        # Add to food_data array
        patient['food_data'].append(food_entry)
        
        # Update patient document
        result = db.patients_collection.update_one(
            {"patient_id": user_id},
            {"$set": {"food_data": patient['food_data']}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Food entry saved successfully for user: {user_id}")
            return jsonify({
                'success': True,
                'message': 'Food entry saved successfully',
                'food_entry': food_entry,
                'total_entries': len(patient['food_data'])
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save food entry'
            }), 500
            
    except Exception as e:
        print(f"[ERROR] Error saving food entry: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_food_entries_service(user_id):
    """Get food entries from patient's food_data array - EXACT from line 6987"""
    try:
        print(f"[*] Getting food entries for user ID: {user_id}")
        
        # Find patient
        patient = db.patients_collection.find_one({"patient_id": user_id})
        if not patient:
            return jsonify({
                'success': False,
                'message': f'Patient not found with ID: {user_id}'
            }), 404
        
        # Get food_data array
        food_data = patient.get('food_data', [])
        
        # Sort by timestamp (most recent first)
        food_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"[OK] Retrieved {len(food_data)} food entries for user: {user_id}")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'food_data': food_data,
            'total_entries': len(food_data)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting food entries: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def debug_food_data_service(user_id):
    """Debug endpoint to check food data structure - EXACT from line 7023"""
    try:
        print(f"[*] Debug food data for user ID: {user_id}")
        
        # Find patient
        patient = db.patients_collection.find_one({"patient_id": user_id})
        if not patient:
            return jsonify({
                'success': False,
                'message': f'Patient not found with ID: {user_id}'
            }), 404
        
        # Get food_data array
        food_data = patient.get('food_data', [])
        
        # Analyze data structure
        basic_entries = [entry for entry in food_data if entry.get('type') == 'basic_entry']
        gpt4_analyses = [entry for entry in food_data if entry.get('type') == 'gpt4_analysis']
        
        debug_info = {
            'user_id': user_id,
            'total_food_entries': len(food_data),
            'basic_entries_count': len(basic_entries),
            'gpt4_analyses_count': len(gpt4_analyses),
            'food_data_structure': {
                'has_food_data_field': 'food_data' in patient,
                'food_data_type': type(food_data).__name__,
                'food_data_length': len(food_data) if isinstance(food_data, list) else 'Not a list'
            },
            'sample_entries': food_data[:3] if food_data else []
        }
        
        print(f"[OK] Debug info generated for user: {user_id}")
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error in debug food data: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def get_food_history_service(patient_id):
    """Get food history for a patient - EXACT from line 2839"""
    try:
        print(f"[*] Getting food history for patient ID: {patient_id}")
        
        # Find patient by Patient ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({'success': False, 'message': f'Patient not found with ID: {patient_id}'}), 404
        
        # Get food logs from patient document
        food_logs = patient.get('food_logs', [])
        
        # Sort by newest first
        food_logs.sort(key=lambda x: x.get('createdAt', datetime.min), reverse=True)
        
        # Convert datetime objects to strings for JSON serialization
        for entry in food_logs:
            if 'createdAt' in entry:
                entry['createdAt'] = entry['createdAt'].isoformat()
        
        print(f"[OK] Retrieved {len(food_logs)} food entries for patient: {patient_id}")
        
        return jsonify({
            'success': True,
            'patientId': patient_id,
            'food_logs': food_logs,
            'totalEntries': len(food_logs)
        }), 200
        
    except Exception as e:
        print(f"Error getting food history: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
