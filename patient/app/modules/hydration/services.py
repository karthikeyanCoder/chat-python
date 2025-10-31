"""
Hydration Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 7272-7940
Business logic for hydration tracking, goals, reminders, analytics

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime, date, timedelta
import uuid
from app.core.database import db


def save_hydration_intake_service(data, authenticated_patient_id):
    """Save hydration intake record - EXACT from line 7275"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        # Validate required fields
        if not data or 'hydration_type' not in data or 'amount_ml' not in data:
            return jsonify({
                'success': False,
                'message': 'hydration_type and amount_ml are required'
            }), 400
        
        # Get user_id from request body (dynamic patient_id)
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id is required in request body'
            }), 400
        
        # Debug logging
        print(f"[*] DEBUG: authenticated_patient_id from JWT: '{authenticated_patient_id}'")
        print(f"[*] DEBUG: user_id from request body: '{user_id}'")
        print(f"[*] DEBUG: Are they equal? {user_id == authenticated_patient_id}")
        print(f"[*] DEBUG: user_id type: {type(user_id)}, authenticated_patient_id type: {type(authenticated_patient_id)}")
        
        # Validate that the user_id matches the authenticated patient_id
        # Note: You can comment out this validation if you want to allow any patient_id
        if user_id != authenticated_patient_id:
            print(f"[WARN] WARNING: user_id mismatch - JWT: '{authenticated_patient_id}', Body: '{user_id}'")
            # Uncomment the next 3 lines to enforce strict validation:
            # return jsonify({
            #     'success': False,
            #     'message': f'user_id does not match authenticated patient. JWT: "{authenticated_patient_id}", Body: "{user_id}"'
            # }), 403
        
        # Use the user_id from request body as the patient_id
        patient_id = user_id
        
        # Check if patient exists
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Create hydration record (following appointment pattern)
        hydration_record = {
            "hydration_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "hydration_type": data['hydration_type'],
            "amount_ml": float(data['amount_ml']),
            "amount_oz": float(data['amount_ml']) * 0.033814,
            "notes": data.get('notes', ''),
            "temperature": data.get('temperature', 'room_temperature'),
            "additives": data.get('additives', []),
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        print(f"[*] Saving hydration intake to patient {patient_id} (from user_id: {user_id}): {hydration_record['hydration_id']}")
        
        # Add hydration record to patient's hydration_records array (same as appointments)
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"hydration_records": hydration_record}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Hydration intake saved to Patient_test collection for patient {patient_id} (dynamic user_id: {user_id})")
            
            return jsonify({
                "success": True,
                "data": hydration_record,
                "message": "Hydration intake saved successfully to Patient_test collection"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to save hydration intake"
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Error saving hydration intake: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to save hydration intake: {str(e)}"
        }), 500


def get_hydration_history_service(patient_id, days=7):
    """Get hydration intake history - EXACT from line 7369"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting hydration history for patient {patient_id} - days: {days}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration records from patient document (same as appointments)
        hydration_records = patient.get('hydration_records', [])
        print(f"[*] Found {len(hydration_records)} total hydration records for patient {patient_id}")
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_records = []
        for record in hydration_records:
            record_timestamp = record.get('timestamp', '')
            if record_timestamp:
                try:
                    record_date = datetime.fromisoformat(record_timestamp.replace('Z', '+00:00'))
                    if record_date >= cutoff_date:
                        filtered_records.append(record)
                except ValueError:
                    # Skip records with invalid timestamp format
                    continue
        
        # Sort by timestamp (newest first)
        filtered_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"[OK] Found {len(filtered_records)} filtered hydration records for patient {patient_id}")
        
        return jsonify({
            "success": True,
            "data": filtered_records,
            "total_count": len(filtered_records),
            "patient_id": patient_id,
            "message": f"Retrieved {len(filtered_records)} hydration records from Patient_test collection"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving hydration history: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve hydration history: {str(e)}"
        }), 500


def get_daily_hydration_stats_service(patient_id, target_date_str=None):
    """Get daily hydration statistics - EXACT from line 7425"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        print(f"[*] Getting hydration stats for patient {patient_id} - date: {target_date}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration records and goal from patient document
        hydration_records = patient.get('hydration_records', [])
        hydration_goal = patient.get('hydration_goal', {})
        
        # Filter records for target date
        target_date_str = target_date.isoformat()
        daily_records = [
            record for record in hydration_records
            if record.get('timestamp', '').startswith(target_date_str)
        ]
        
        # Calculate stats
        total_intake_ml = sum(record.get('amount_ml', 0) for record in daily_records)
        total_intake_oz = sum(record.get('amount_oz', 0) for record in daily_records)
        
        goal_ml = hydration_goal.get('daily_goal_ml', 2000)
        goal_oz = hydration_goal.get('daily_goal_oz', 67.6)
        goal_percentage = (total_intake_ml / goal_ml * 100) if goal_ml > 0 else 0
        
        # Calculate intake by type
        intake_by_type = {}
        for record in daily_records:
            hydration_type = record.get('hydration_type', 'water')
            amount = record.get('amount_ml', 0)
            intake_by_type[hydration_type] = intake_by_type.get(hydration_type, 0) + amount
        
        stats = {
            "patient_id": patient_id,
            "date": target_date.isoformat(),
            "total_intake_ml": total_intake_ml,
            "total_intake_oz": total_intake_oz,
            "goal_ml": goal_ml,
            "goal_oz": goal_oz,
            "goal_percentage": round(goal_percentage, 1),
            "intake_by_type": intake_by_type,
            "is_goal_met": total_intake_ml >= goal_ml,
            "records_count": len(daily_records)
        }
        
        print(f"[OK] Calculated hydration stats for patient {patient_id}: {total_intake_ml}ml / {goal_ml}ml ({goal_percentage:.1f}%)")
        
        return jsonify({
            "success": True,
            "data": stats,
            "message": "Hydration statistics retrieved successfully from Patient_test collection"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving hydration stats: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve hydration stats: {str(e)}"
        }), 500


def set_hydration_goal_service(data, patient_id):
    """Set or update hydration goal - EXACT from line 7502"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        # Validate required fields
        if not data or 'daily_goal_ml' not in data:
            return jsonify({
                'success': False,
                'message': 'daily_goal_ml is required'
            }), 400
        
        # Check if patient exists
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Create hydration goal data
        goal_data = {
            "daily_goal_ml": float(data['daily_goal_ml']),
            "daily_goal_oz": float(data['daily_goal_ml']) * 0.033814,
            "reminder_enabled": data.get('reminder_enabled', True),
            "reminder_times": data.get('reminder_times', ["08:00", "12:00", "16:00", "20:00"]),
            "start_date": date.today().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        print(f"[*] Setting hydration goal for patient {patient_id}: {goal_data['daily_goal_ml']}ml")
        
        # Update patient's hydration goal (same pattern as appointments)
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": {"hydration_goal": goal_data}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Hydration goal saved to Patient_test collection for patient {patient_id}")
            
            return jsonify({
                "success": True,
                "data": goal_data,
                "message": "Hydration goal set successfully in Patient_test collection"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to set hydration goal"
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Error setting hydration goal: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to set hydration goal: {str(e)}"
        }), 500


def get_hydration_goal_service(patient_id):
    """Get current hydration goal - EXACT from line 7565"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting hydration goal for patient {patient_id}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration goal from patient document
        hydration_goal = patient.get('hydration_goal', {})
        
        if not hydration_goal:
            # Return default goal if none set
            default_goal = {
                "patient_id": patient_id,
                "daily_goal_ml": 2000,
                "daily_goal_oz": 67.6,
                "start_date": date.today().isoformat(),
                "is_active": True,
                "reminder_enabled": True,
                "reminder_times": ["08:00", "12:00", "16:00", "20:00"]
            }
            return jsonify({
                "success": True,
                "data": default_goal,
                "message": "No hydration goal set, returning default"
            }), 200
        
        print(f"[OK] Found hydration goal for patient {patient_id}: {hydration_goal['daily_goal_ml']}ml")
        
        return jsonify({
            "success": True,
            "data": hydration_goal,
            "message": "Hydration goal retrieved successfully from Patient_test collection"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving hydration goal: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve hydration goal: {str(e)}"
        }), 500


def create_hydration_reminder_service(data, patient_id):
    """Create hydration reminder - EXACT from line 7617"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        # Validate required fields
        if not data or 'reminder_time' not in data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'reminder_time and message are required'
            }), 400
        
        # Check if patient exists
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Create reminder data
        reminder_data = {
            "reminder_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "reminder_time": data['reminder_time'],
            "message": data['message'],
            "days_of_week": data.get('days_of_week', [0, 1, 2, 3, 4, 5, 6]),
            "is_enabled": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        print(f"[*] Creating hydration reminder for patient {patient_id}: {reminder_data['reminder_id']}")
        
        # Add reminder to patient's hydration_reminders array (same as appointments)
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"hydration_reminders": reminder_data}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Hydration reminder saved to Patient_test collection for patient {patient_id}")
            
            return jsonify({
                "success": True,
                "data": reminder_data,
                "message": "Hydration reminder created successfully in Patient_test collection"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to create hydration reminder"
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Error creating hydration reminder: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to create hydration reminder: {str(e)}"
        }), 500


def get_hydration_reminders_service(patient_id):
    """Get all hydration reminders - EXACT from line 7681"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting hydration reminders for patient {patient_id}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration reminders from patient document
        reminders = patient.get('hydration_reminders', [])
        
        print(f"[OK] Found {len(reminders)} hydration reminders for patient {patient_id}")
        
        return jsonify({
            "success": True,
            "data": {"reminders": reminders},
            "total_count": len(reminders),
            "patient_id": patient_id,
            "message": f"Retrieved {len(reminders)} hydration reminders from Patient_test collection"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving hydration reminders: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve hydration reminders: {str(e)}"
        }), 500


def get_hydration_analysis_service(patient_id, days=7):
    """Get hydration analysis and insights - EXACT from line 7718"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting hydration analysis for patient {patient_id} - days: {days}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration records from patient document
        hydration_records = patient.get('hydration_records', [])
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_records = []
        for record in hydration_records:
            record_timestamp = record.get('timestamp', '')
            if record_timestamp:
                try:
                    record_date = datetime.fromisoformat(record_timestamp.replace('Z', '+00:00'))
                    if record_date >= cutoff_date:
                        filtered_records.append(record)
                except ValueError:
                    continue
        
        # Calculate analysis
        total_intake = sum(record.get('amount_ml', 0) for record in filtered_records)
        avg_daily_intake = total_intake / days if days > 0 else 0
        
        # Group by type
        intake_by_type = {}
        for record in filtered_records:
            hydration_type = record.get('hydration_type', 'water')
            amount = record.get('amount_ml', 0)
            intake_by_type[hydration_type] = intake_by_type.get(hydration_type, 0) + amount
        
        analysis = {
            "patient_id": patient_id,
            "period_days": days,
            "total_intake_ml": total_intake,
            "avg_daily_intake_ml": round(avg_daily_intake, 1),
            "intake_by_type": intake_by_type,
            "records_analyzed": len(filtered_records),
            "analysis_date": datetime.now().isoformat()
        }
        
        print(f"[OK] Hydration analysis for patient {patient_id}: {avg_daily_intake:.1f}ml/day average")
        
        return jsonify({
            "success": True,
            "data": analysis,
            "message": "Hydration analysis retrieved successfully from Patient_test collection"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving hydration analysis: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve hydration analysis: {str(e)}"
        }), 500


def get_weekly_hydration_report_service(patient_id):
    """Get weekly hydration report - EXACT from line 7788"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting weekly hydration report for patient {patient_id}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration records and goal from patient document
        hydration_records = patient.get('hydration_records', [])
        hydration_goal = patient.get('hydration_goal', {})
        
        # Get last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Filter records for the week
        weekly_records = []
        for record in hydration_records:
            record_timestamp = record.get('timestamp', '')
            if record_timestamp:
                try:
                    record_date = datetime.fromisoformat(record_timestamp.replace('Z', '+00:00')).date()
                    if start_date <= record_date <= end_date:
                        weekly_records.append(record)
                except ValueError:
                    continue
        
        # Calculate daily stats
        daily_stats = {}
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.isoformat()
            daily_records = [r for r in weekly_records if r.get('timestamp', '').startswith(date_str)]
            daily_intake = sum(record.get('amount_ml', 0) for record in daily_records)
            daily_stats[date_str] = {
                "date": date_str,
                "intake_ml": daily_intake,
                "records_count": len(daily_records)
            }
        
        # Calculate weekly totals
        total_weekly_intake = sum(record.get('amount_ml', 0) for record in weekly_records)
        avg_daily_intake = total_weekly_intake / 7
        goal_ml = hydration_goal.get('daily_goal_ml', 2000)
        weekly_goal = goal_ml * 7
        goal_achievement = (total_weekly_intake / weekly_goal * 100) if weekly_goal > 0 else 0
        
        report = {
            "patient_id": patient_id,
            "week_start": start_date.isoformat(),
            "week_end": end_date.isoformat(),
            "total_weekly_intake_ml": total_weekly_intake,
            "avg_daily_intake_ml": round(avg_daily_intake, 1),
            "weekly_goal_ml": weekly_goal,
            "goal_achievement_percentage": round(goal_achievement, 1),
            "daily_stats": daily_stats,
            "records_analyzed": len(weekly_records)
        }
        
        print(f"[OK] Weekly hydration report for patient {patient_id}: {total_weekly_intake}ml total, {avg_daily_intake:.1f}ml/day average")
        
        return jsonify({
            "success": True,
            "data": report,
            "message": "Weekly hydration report retrieved successfully from Patient_test collection"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving weekly hydration report: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve weekly hydration report: {str(e)}"
        }), 500


def get_hydration_tips_service(patient_id):
    """Get personalized hydration tips - EXACT from line 7872"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting hydration tips for patient {patient_id}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get hydration goal and recent records
        hydration_goal = patient.get('hydration_goal', {})
        hydration_records = patient.get('hydration_records', [])
        
        # Get today's intake
        today = date.today().isoformat()
        today_records = [r for r in hydration_records if r.get('timestamp', '').startswith(today)]
        today_intake = sum(record.get('amount_ml', 0) for record in today_records)
        
        goal_ml = hydration_goal.get('daily_goal_ml', 2000)
        progress = (today_intake / goal_ml * 100) if goal_ml > 0 else 0
        
        # Generate personalized tips based on progress
        tips = []
        if progress < 25:
            tips = [
                "Start your day with a large glass of water",
                "Set hourly reminders to drink water",
                "Keep a water bottle visible on your desk",
                "Add lemon or cucumber to make water more appealing"
            ]
        elif progress < 50:
            tips = [
                "You're making good progress! Keep it up",
                "Try drinking water before each meal",
                "Set a goal to finish your water bottle by lunch",
                "Consider herbal teas as a hydrating alternative"
            ]
        elif progress < 75:
            tips = [
                "Great job! You're more than halfway to your goal",
                "Try drinking water between meals",
                "Consider adding electrolytes if you're active",
                "Eat water-rich fruits and vegetables"
            ]
        else:
            tips = [
                "Excellent! You're close to or have met your goal",
                "Maintain this great habit",
                "Remember to hydrate during exercise",
                "Monitor your urine color as a hydration indicator"
            ]
        
        tips_data = {
            "patient_id": patient_id,
            "today_intake_ml": today_intake,
            "goal_ml": goal_ml,
            "progress_percentage": round(progress, 1),
            "tips": tips,
            "generated_at": datetime.now().isoformat()
        }
        
        print(f"[OK] Generated {len(tips)} hydration tips for patient {patient_id} (progress: {progress:.1f}%)")
        
        return jsonify({
            "success": True,
            "data": tips_data,
            "message": "Hydration tips retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving hydration tips: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve hydration tips: {str(e)}"
        }), 500
