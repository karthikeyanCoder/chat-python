"""
Appointments Module Services - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py lines 8727-9604
Business logic for patient and doctor appointment management

NO CHANGES TO LOGIC - Exact extraction, converted to function-based
"""

from flask import jsonify
from datetime import datetime
from bson import ObjectId
from app.core.database import db
import requests
import os


# SLOT VALIDATION SERVICE

def validate_slot_availability(doctor_id, appointment_date, slot_id, consultation_type=None):
    """Validate slot availability by calling doctor availability API - uses consultation_type"""
    try:
        # Validate required inputs
        if not doctor_id or not appointment_date or not slot_id:
            return {
                'success': False,
                'error': 'Missing required parameters for slot validation'
            }

        # Get doctor module URL
        doctor_module_url = os.environ.get('DOCTOR_MODULE_URL')
        if not doctor_module_url:
            return {
                'success': False,
                'error': 'DOCTOR_MODULE_URL not configured'
            }

        # Use date-level endpoint (not by-type) and pass consultation_type as query param
        url = f"{doctor_module_url}/public/doctor/{doctor_id}/availability/{appointment_date}"
        if consultation_type:
            url += f"?consultation_type={consultation_type}"
        print(f"[*] Validating slot {slot_id} via: {url}")

        # Make API request
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Response data: {data}")

            # Search for slot_id across all types in availability response
            availability_list = data.get('availability', [])
            if isinstance(availability_list, list) and len(availability_list) > 0:
                for avail_doc in availability_list:
                    types_list = avail_doc.get('types', [])
                    for type_obj in types_list:
                        slots = type_obj.get('slots', [])
                        for slot in slots:
                            print(f"[DEBUG] Checking slot_id: {slot.get('slot_id')}")
                            if slot.get('slot_id') == slot_id:
                                print(f"[OK] Slot {slot_id} found and available")
                                # Extract appointment type from found slot's parent
                                slot_with_type = slot.copy()
                                slot_with_type['appointment_type'] = type_obj.get('type')
                                return {
                                    'success': True,
                                    'slot': slot_with_type
                                }

                # Slot not found
                return {
                    'success': False,
                    'error': f'Slot {slot_id} not found in available slots'
                }

            else:
                return {
                    'success': False,
                    'error': 'No slots found for the specified criteria'
                }

        else:
            return {
                'success': False,
                'error': f'Failed to validate slot: HTTP {response.status_code}'
            }

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error validating slot: {str(e)}")
        return {
            'success': False,
            'error': f'Network error: {str(e)}'
        }

    except Exception as e:
        print(f"[ERROR] Error validating slot: {str(e)}")
        return {
            'success': False,
            'error': f'Validation error: {str(e)}'
        }

def book_slot_in_doctor_availability(doctor_id, appointment_date, slot_id, patient_id, appointment_id, consultation_type=None):
    """Book a slot in the doctor availability system"""
    try:
        if not doctor_id or not appointment_date or not slot_id or not patient_id or not appointment_id:
            return {
                'success': False,
                'error': 'Missing required parameters for slot booking'
            }
        
        # Get doctor module URL from environment or use default
        doctor_module_url = os.environ.get('DOCTOR_MODULE_URL')
        
        # Call doctor availability API to book the slot - pass consultation_type as query param
        url = f"{doctor_module_url}/doctor/{doctor_id}/availability/{appointment_date}/book-slot"
        if consultation_type:
            url += f"?consultation_type={consultation_type}"
        
        booking_data = {
            "slot_id": slot_id,
            "patient_id": patient_id,
            "appointment_id": appointment_id
        }
        
        print(f"[*] Booking slot {slot_id} via: {url}")
        
        response = requests.post(url, json=booking_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"[OK] Slot {slot_id} booked successfully")
                return {
                    'success': True,
                    'message': 'Slot booked successfully'
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', 'Failed to book slot')
                }
        else:
            return {
                'success': False,
                'error': f'Failed to book slot: HTTP {response.status_code}'
            }
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error booking slot: {str(e)}")
        return {
            'success': False,
            'error': f'Network error: {str(e)}'
        }
    except Exception as e:
        print(f"[ERROR] Error booking slot: {str(e)}")
        return {
            'success': False,
            'error': f'Booking error: {str(e)}'
        }

def cancel_slot_in_doctor_availability(doctor_id, appointment_date, slot_id, appointment_id, cancellation_reason="Cancelled by patient", patient_token=None, consultation_type=None):
    """Cancel/unbook a slot in the doctor availability system"""
    try:
        if not doctor_id or not appointment_date or not slot_id or not appointment_id:
            return {
                'success': False,
                'error': 'Missing required parameters for slot cancellation'
            }
        
        # Get doctor module URL from environment or use default
        doctor_module_url = os.environ.get('DOCTOR_MODULE_URL')
        
        # Call doctor availability API to cancel the slot
        url = f"{doctor_module_url}/doctor/{doctor_id}/availability/{appointment_date}/{slot_id}/cancel"
        if consultation_type:
            url += f"?consultation_type={consultation_type}"
        
        cancel_data = {
            "appointment_id": appointment_id,
            "cancellation_reason": cancellation_reason
        }
        
        # Prepare headers with Authorization token
        headers = {}
        if patient_token:
            headers['Authorization'] = f'Bearer {patient_token}'
        
        print(f"[*] Cancelling slot {slot_id} via: {url}")
        
        response = requests.post(url, json=cancel_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"[OK] Slot {slot_id} cancelled successfully")
                return {
                    'success': True,
                    'message': 'Slot cancelled successfully'
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', 'Failed to cancel slot')
                }
        else:
            return {
                'success': False,
                'error': f'Failed to cancel slot: HTTP {response.status_code}'
            }
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error cancelling slot: {str(e)}")
        return {
            'success': False,
            'error': f'Network error: {str(e)}'
        }
    except Exception as e:
        print(f"[ERROR] Error cancelling slot: {str(e)}")
        return {
            'success': False,
            'error': f'Cancellation error: {str(e)}'
        }


# PATIENT APPOINTMENT SERVICES

def get_patient_appointments_service(patient_id, date=None, status=None, consultation_type=None, appointment_type=None):
    """Get all appointments for the authenticated patient - EXACT from line 8727"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting appointments for patient {patient_id} - date: {date}, status: {status}, type: {consultation_type}, appointment_type: {appointment_type}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        appointments = patient.get('appointments', [])
        print(f"[*] Found {len(appointments)} total appointments for patient {patient_id}")
        
        # Filter appointments based on query parameters
        filtered_appointments = []
        for appointment in appointments:
            # Filter by date if provided
            if date and appointment.get('appointment_date') != date:
                continue
            
            # Filter by status if provided
            if status is not None and appointment.get('appointment_status') != status:
                continue
            
            # Filter by consultation type if provided (Follow-up, Consultation, etc.)
            if consultation_type and appointment.get('type') != consultation_type:
                continue
            
            # Filter by appointment type (Video Call, In-person) if provided
            if appointment_type and appointment.get('appointment_type') != appointment_type:
                continue
            
            # Add patient info to appointment
            appointment_data = appointment.copy()
            appointment_data['patient_id'] = patient_id
            appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
            
            filtered_appointments.append(appointment_data)
        
        # Sort by appointment date
        filtered_appointments.sort(key=lambda x: x.get('appointment_date', ''))
        
        print(f"[OK] Found {len(filtered_appointments)} appointments for patient {patient_id}")
        
        return jsonify({
            "appointments": filtered_appointments,
            "total_count": len(filtered_appointments),
            "patient_id": patient_id,
            "message": "Appointments retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving patient appointments: {str(e)}")
        return jsonify({"error": f"Failed to retrieve appointments: {str(e)}"}), 500


def create_patient_appointment_service(data, patient_id):
    """Create a new appointment request - Enhanced with slot validation"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Patient {patient_id} creating appointment request - data: {data}")
        
        # Validate required fields - type is optional
        required_fields = ['appointment_date', 'appointment_time', 'appointment_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Enhanced slot validation if slot_id is provided
        slot_data = None
        if data.get('slot_id'):
            print(f"[*] Validating slot_id: {data['slot_id']}")
            slot_validation = validate_slot_availability(
                data.get('doctor_id', ''),
                data['appointment_date'],
                data['slot_id'],
                consultation_type=data.get('appointment_type')  # Pass appointment_type as consultation_type
            )
            
            if not slot_validation['success']:
                return jsonify({"error": f"Slot validation failed: {slot_validation['error']}"}), 400
            
            slot_data = slot_validation['slot']
            print(f"[OK] Slot validated: {slot_data['start_time']} - {slot_data['end_time']}")
            
            # Extract appointment type from validated slot if type not provided
            if not data.get('type') and slot_data.get('appointment_type'):
                inferred_type = slot_data.get('appointment_type')
                data['type'] = inferred_type
                print(f"[*] Inferred appointment type from slot: {inferred_type}")
            
            # Use slot timing if available
            if slot_data.get('start_time'):
                data['appointment_time'] = slot_data['start_time']
            if slot_data.get('end_time'):
                data['end_time'] = slot_data['end_time']
            if slot_data.get('duration_mins'):
                data['duration_mins'] = slot_data['duration_mins']
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        print(f"[OK] Patient found: {patient.get('first_name', '')} {patient.get('last_name', '')}")
        
        # Generate unique appointment ID
        appointment_id = str(ObjectId())
        
        # Create appointment object with SEPARATE type and appointment_type
        # type is optional - use inferred from slot or default to "General Consultation"
        appointment_type_value = data.get('type', 'General Consultation')
        appointment = {
            "appointment_id": appointment_id,
            "appointment_date": data["appointment_date"],
            "appointment_time": data["appointment_time"],
            "type": appointment_type_value,  # Consultation type: "Follow-up", "Consultation", "Check-up", "Emergency" (optional)
            "appointment_type": data["appointment_type"],  # Mode: "Online", "In-Person"
            "appointment_status": "pending",  # Patient requests start as pending
            "notes": data.get("notes", ""),
            "patient_notes": data.get("patient_notes", ""),
            "doctor_id": data.get("doctor_id", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "requested_by": "patient"
        }
        
        # Add slot information if slot_id was provided
        if data.get('slot_id'):
            appointment["slot_id"] = data["slot_id"]
            if slot_data:
                appointment["slot_start_time"] = slot_data.get("start_time")
                appointment["slot_end_time"] = slot_data.get("end_time")
                appointment["slot_duration_mins"] = slot_data.get("duration_mins")
                appointment["slot_price"] = slot_data.get("price")
                appointment["slot_currency"] = slot_data.get("currency")
        
        print(f"[*] Saving appointment request to patient {patient_id}: {appointment}")
        
        # Add appointment to patient's appointments array
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"appointments": appointment}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment request saved successfully!")
            
            # Book the slot in doctor availability system if slot_id was provided
            final_status = "pending"
            if data.get('slot_id'):
                print(f"[*] Booking slot {data['slot_id']} in doctor availability system")
                booking_result = book_slot_in_doctor_availability(
                    data.get('doctor_id', ''),
                    data['appointment_date'],
                    data['slot_id'],
                    patient_id,
                    appointment_id,
                    consultation_type=data.get('appointment_type')
                )
                
                if booking_result.get('success'):
                    # Mark appointment as booked
                    final_status = "booked"
                    db.patients_collection.update_one(
                        {"patient_id": patient_id, "appointments.appointment_id": appointment_id},
                        {"$set": {"appointments.$.appointment_status": "booked", "appointments.$.updated_at": datetime.now().isoformat()}}
                    )
                else:
                    final_status = "not_booked"
                    print(f"[ERROR] Failed to book slot: {booking_result.get('error')}")
                    # Appointment remains but slot not locked
            
            response_data = {
                "appointment_id": appointment_id,
                "message": "Appointment request created successfully",
                "status": final_status,
                "type": data.get("type", "General Consultation"),
                "appointment_type": data["appointment_type"]
            }
            
            # Add slot information to response if slot_id was provided
            if data.get('slot_id'):
                response_data["slot_id"] = data["slot_id"]
                if slot_data:
                    response_data["slot_start_time"] = slot_data.get("start_time")
                    response_data["slot_end_time"] = slot_data.get("end_time")
                    response_data["slot_duration_mins"] = slot_data.get("duration_mins")
                    response_data["slot_price"] = slot_data.get("price")
                    response_data["slot_currency"] = slot_data.get("currency")
            
            return jsonify(response_data), 201
        else:
            return jsonify({"error": "Failed to save appointment request"}), 500
        
    except Exception as e:
        print(f"[ERROR] Error creating patient appointment: {str(e)}")
        return jsonify({"error": f"Failed to create appointment: {str(e)}"}), 500


def get_patient_appointment_service(appointment_id, patient_id):
    """Get specific appointment details - EXACT from line 8865"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting appointment {appointment_id} for patient {patient_id}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Find the specific appointment
        appointments = patient.get('appointments', [])
        appointment = None
        for apt in appointments:
            if apt.get('appointment_id') == appointment_id:
                appointment = apt
                break
        
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Add patient info to appointment
        appointment_data = appointment.copy()
        appointment_data['patient_id'] = patient_id
        appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
        
        print(f"[OK] Found appointment: {appointment_data}")
        
        return jsonify({
            "appointment": appointment_data,
            "message": "Appointment retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving patient appointment: {str(e)}")
        return jsonify({"error": f"Failed to retrieve appointment: {str(e)}"}), 500


def update_patient_appointment_service(appointment_id, data, patient_id, patient_token=None):
    """Update appointment details - Handle rescheduling with slot management"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Patient {patient_id} updating appointment {appointment_id} with data: {data}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Find the appointment
        appointments = patient.get('appointments', [])
        appointment_index = None
        current_appointment = None
        
        for idx, appt in enumerate(appointments):
            if appt.get('appointment_id') == appointment_id:
                appointment_index = idx
                current_appointment = appt
                break
        
        if appointment_index is None:
            return jsonify({"error": "Appointment not found"}), 404
        
        # [WARN] CRITICAL BUSINESS RULE: Cannot update approved appointments
        if current_appointment.get('appointment_status') == 'approved':
            return jsonify({
                "error": "Cannot update approved appointments",
                "message": "This appointment has been approved by the doctor. Please cancel this appointment and create a new one if you need to make changes.",
                "action_required": "cancel_and_recreate",
                "current_status": "approved"
            }), 403  # 403 Forbidden
        
        # Check if rescheduling to a different date or slot
        old_slot_id = current_appointment.get('slot_id')
        old_appointment_date = current_appointment.get('appointment_date')
        new_appointment_date = data.get('appointment_date')
        new_slot_id = data.get('slot_id')
        
        # If changing date or slot, need to handle slot unbooking and rebooking
        if old_slot_id and (new_appointment_date != old_appointment_date or new_slot_id):
            print(f"[*] Rescheduling appointment - handling slot changes")
            
            # Cancel old slot in doctor module
            cancel_result = cancel_slot_in_doctor_availability(
                current_appointment.get('doctor_id', ''),
                old_appointment_date,
                old_slot_id,
                appointment_id,
                "Rescheduled by patient",
                patient_token,
                consultation_type=current_appointment.get('appointment_type')
            )
            
            if not cancel_result['success']:
                print(f"[WARNING] Failed to cancel old slot: {cancel_result['error']}")
                # Continue anyway - this might be a valid case if slot was already unbooked
        
        # Prepare update data - patients can only update certain fields
        update_fields = {}
        allowed_fields = ['appointment_date', 'appointment_time', 'type', 'appointment_type', 'patient_notes', 'notes']
        
        for field in allowed_fields:
            if field in data:
                update_fields[f"appointments.{appointment_index}.{field}"] = data[field]
        
        # Handle new slot booking if new_slot_id provided
        if new_slot_id and new_appointment_date:
            # Validate and book new slot - use appointment_type as consultation_type
            consultation_type_for_new = data.get('appointment_type') or current_appointment.get('appointment_type')
            slot_validation = validate_slot_availability(
                current_appointment.get('doctor_id', ''),
                new_appointment_date,
                new_slot_id,
                consultation_type=consultation_type_for_new
            )
            
            if not slot_validation['success']:
                return jsonify({"error": f"New slot validation failed: {slot_validation['error']}"}), 400
            
            # Extract type from slot if not provided
            if not data.get('type') and slot_validation['slot'].get('appointment_type'):
                data['type'] = slot_validation['slot'].get('appointment_type')
            
            # Book new slot in doctor module
            booking_result = book_slot_in_doctor_availability(
                current_appointment.get('doctor_id', ''),
                new_appointment_date,
                new_slot_id,
                patient_id,
                appointment_id,
                consultation_type=consultation_type_for_new
            )
            
            if not booking_result['success']:
                print(f"[ERROR] Failed to book new slot: {booking_result['error']}")
                # Rollback: try to book old slot back
                if old_slot_id:
                    cancel_slot_in_doctor_availability(
                        current_appointment.get('doctor_id', ''),
                        old_appointment_date,
                        old_slot_id,
                        appointment_id,
                        "Reschedule failed",
                        patient_token
                    )
                return jsonify({"error": f"Failed to book new slot: {booking_result['error']}"}), 400
            
            # Update slot information
            slot_data = slot_validation['slot']
            update_fields[f"appointments.{appointment_index}.slot_id"] = new_slot_id
            update_fields[f"appointments.{appointment_index}.slot_start_time"] = slot_data.get("start_time")
            update_fields[f"appointments.{appointment_index}.slot_end_time"] = slot_data.get("end_time")
            update_fields[f"appointments.{appointment_index}.slot_duration_mins"] = slot_data.get("duration_mins")
            update_fields[f"appointments.{appointment_index}.slot_price"] = slot_data.get("price")
            update_fields[f"appointments.{appointment_index}.slot_currency"] = slot_data.get("currency")
        
        if not update_fields and not (old_slot_id and (new_appointment_date != old_appointment_date or new_slot_id)):
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Add updated_at timestamp
        update_fields[f"appointments.{appointment_index}.updated_at"] = datetime.now().isoformat()
        
        print(f"[*] Updating appointment fields: {update_fields}")
        
        # Update appointment in database
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": update_fields}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment {appointment_id} updated successfully!")
            
            # Get updated appointment
            updated_patient = db.patients_collection.find_one({"patient_id": patient_id})
            updated_appointment = updated_patient['appointments'][appointment_index]
            
            return jsonify({
                "message": "Appointment updated successfully",
                "appointment": updated_appointment,
                "appointment_id": appointment_id
            }), 200
        else:
            return jsonify({"error": "No changes made to appointment"}), 400
        
    except Exception as e:
        print(f"[ERROR] Error updating patient appointment: {str(e)}")
        return jsonify({"error": f"Failed to update appointment: {str(e)}"}), 500


def cancel_patient_appointment_service(appointment_id, patient_id, patient_token=None):
    """Cancel/delete appointment and unbook doctor slot"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Patient {patient_id} cancelling appointment {appointment_id}")
        
        # First, get the appointment to extract slot info
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Find the appointment
        appointments = patient.get('appointments', [])
        appointment_to_cancel = None
        
        for appt in appointments:
            if appt.get('appointment_id') == appointment_id:
                appointment_to_cancel = appt
                break
        
        if not appointment_to_cancel:
            return jsonify({"error": "Appointment not found"}), 404
        
        # If appointment has a slot_id, cancel the slot in doctor module first
        if appointment_to_cancel.get('slot_id'):
            print(f"[*] Cancelling slot {appointment_to_cancel.get('slot_id')} in doctor availability system")
            cancel_result = cancel_slot_in_doctor_availability(
                appointment_to_cancel.get('doctor_id', ''),
                appointment_to_cancel.get('appointment_date', ''),
                appointment_to_cancel.get('slot_id'),
                appointment_id,
                "Cancelled by patient",
                patient_token,
                consultation_type=appointment_to_cancel.get('appointment_type')
            )
            
            if not cancel_result['success']:
                print(f"[WARNING] Failed to cancel slot in doctor module: {cancel_result['error']}")
                # Continue with patient side cancellation anyway
        
        # Remove appointment from patient's appointments array
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$pull": {"appointments": {"appointment_id": appointment_id}}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment {appointment_id} cancelled successfully!")
            return jsonify({
                "message": "Appointment cancelled successfully",
                "appointment_id": appointment_id
            }), 200
        else:
            return jsonify({"error": "Appointment not found or already cancelled"}), 404
        
    except Exception as e:
        print(f"[ERROR] Error cancelling patient appointment: {str(e)}")
        return jsonify({"error": f"Failed to cancel appointment: {str(e)}"}), 500


def get_upcoming_appointments_service(patient_id):
    """Get upcoming appointments - EXACT from line 9027"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting upcoming appointments for patient {patient_id}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        appointments = patient.get('appointments', [])
        today = datetime.now().date()
        
        # Filter upcoming appointments (future dates and active status)
        upcoming_appointments = []
        for appointment in appointments:
            appointment_date_str = appointment.get('appointment_date', '')
            appointment_status = appointment.get('appointment_status', '')
            
            if appointment_status in ['scheduled', 'confirmed', 'booked']:
                try:
                    appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
                    if appointment_date >= today:
                        appointment_data = appointment.copy()
                        appointment_data['patient_id'] = patient_id
                        appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                        upcoming_appointments.append(appointment_data)
                except ValueError:
                    # Skip appointments with invalid date format
                    continue
        
        # Sort by appointment date
        upcoming_appointments.sort(key=lambda x: x.get('appointment_date', ''))
        
        print(f"[OK] Found {len(upcoming_appointments)} upcoming appointments for patient {patient_id}")
        
        return jsonify({
            "upcoming_appointments": upcoming_appointments,
            "total_count": len(upcoming_appointments),
            "patient_id": patient_id,
            "message": "Upcoming appointments retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving upcoming appointments: {str(e)}")
        return jsonify({"error": f"Failed to retrieve upcoming appointments: {str(e)}"}), 500


def get_appointment_history_service(patient_id, status=None, consultation_type=None, appointment_type=None, date=None):
    """Get appointment history with filtering - EXACT from line 9081"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting appointment history for patient {patient_id} - status: {status}, type: {consultation_type}, appointment_type: {appointment_type}, date: {date}")
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        appointments = patient.get('appointments', [])
        print(f"[*] Found {len(appointments)} total appointments for patient {patient_id}")
        
        # Filter appointments based on query parameters
        filtered_appointments = []
        for appointment in appointments:
            # Filter by status if provided
            if status and appointment.get('appointment_status') != status:
                continue
            
            # Filter by consultation type if provided (Follow-up, Consultation, etc.)
            if consultation_type and appointment.get('type') != consultation_type:
                continue
            
            # Filter by appointment type (Video Call, In-person) if provided
            if appointment_type and appointment.get('appointment_type') != appointment_type:
                continue
            
            # Filter by date if provided
            if date and appointment.get('appointment_date') != date:
                continue
            
            # Add patient info to appointment
            appointment_data = appointment.copy()
            appointment_data['patient_id'] = patient_id
            appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
            filtered_appointments.append(appointment_data)
        
        # Sort by appointment date (most recent first)
        filtered_appointments.sort(key=lambda x: x.get('appointment_date', ''), reverse=True)
        
        print(f"[OK] Found {len(filtered_appointments)} appointments in filtered history for patient {patient_id}")
        
        return jsonify({
            "appointment_history": filtered_appointments,
            "total_count": len(filtered_appointments),
            "patient_id": patient_id,
            "filters_applied": {
                "status": status,
                "type": consultation_type,
                "appointment_type": appointment_type,
                "date": date
            },
            "message": "Appointment history retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving appointment history: {str(e)}")
        return jsonify({"error": f"Failed to retrieve appointment history: {str(e)}"}), 500


# DOCTOR APPOINTMENT SERVICES

def get_doctor_appointments_service(date=None, status=None, appointment_type=None, patient_id=None):
    """Get all appointments for doctor management - EXACT from line 9158"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting appointments for doctor - date: {date}, status: {status}, type: {appointment_type}, patient: {patient_id}")
        
        # Build query filter
        query_filter = {}
        if patient_id:
            query_filter["patient_id"] = patient_id
        
        # Get all patients with appointments
        patients = db.patients_collection.find(query_filter)
        
        all_appointments = []
        for patient in patients:
            appointments = patient.get('appointments', [])
            for appointment in appointments:
                # Filter appointments based on query parameters
                if date and appointment.get('appointment_date') != date:
                    continue
                if status and appointment.get('appointment_status') != status:
                    continue
                if appointment_type and appointment.get('appointment_type') != appointment_type:
                    continue
                
                # Add patient info to appointment
                appointment_data = appointment.copy()
                appointment_data['patient_id'] = patient.get('patient_id')
                appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                appointment_data['patient_email'] = patient.get('email', '')
                appointment_data['patient_mobile'] = patient.get('mobile', '')
                
                all_appointments.append(appointment_data)
        
        # Sort by appointment date
        all_appointments.sort(key=lambda x: x.get('appointment_date', ''))
        
        print(f"[OK] Found {len(all_appointments)} appointments for doctor")
        
        return jsonify({
            "appointments": all_appointments,
            "total_count": len(all_appointments),
            "message": "Appointments retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving doctor appointments: {str(e)}")
        return jsonify({"error": f"Failed to retrieve appointments: {str(e)}"}), 500


def create_doctor_appointment_service(data):
    """Create a new appointment by doctor - EXACT from line 9218"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Doctor creating appointment - data: {data}")
        
        # Validate required fields
        required_fields = ['patient_id', 'appointment_date', 'appointment_time', 'appointment_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        patient_id = data['patient_id']
        
        # Get patient document
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        print(f"[OK] Patient found: {patient.get('first_name', '')} {patient.get('last_name', '')}")
        
        # Generate unique appointment ID
        appointment_id = str(ObjectId())
        
        # Create appointment object
        appointment = {
            "appointment_id": appointment_id,
            "appointment_date": data["appointment_date"],
            "appointment_time": data["appointment_time"],
            "appointment_type": data["appointment_type"],
            "appointment_status": "scheduled",  # Doctor creates as scheduled
            "notes": data.get("notes", ""),
            "patient_notes": data.get("patient_notes", ""),
            "doctor_id": data.get("doctor_id", "DOC001"),
            "doctor_notes": data.get("doctor_notes", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "created_by": "doctor"
        }
        
        print(f"[*] Saving appointment to patient {patient_id}: {appointment}")
        
        # Add appointment to patient's appointments array
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$push": {"appointments": appointment}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment created successfully!")
            return jsonify({
                "appointment_id": appointment_id,
                "message": "Appointment created successfully",
                "status": "scheduled"
            }), 201
        else:
            return jsonify({"error": "Failed to create appointment"}), 500
        
    except Exception as e:
        print(f"[ERROR] Error creating doctor appointment: {str(e)}")
        return jsonify({"error": f"Failed to create appointment: {str(e)}"}), 500


def get_doctor_appointment_service(appointment_id):
    """Get specific appointment details for doctor - EXACT from line 9287"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Doctor getting appointment {appointment_id}")
        
        # Find patient with this appointment
        patient = db.patients_collection.find_one({
            "appointments.appointment_id": appointment_id
        })
        if not patient:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Find the specific appointment
        appointments = patient.get('appointments', [])
        appointment = None
        for apt in appointments:
            if apt.get('appointment_id') == appointment_id:
                appointment = apt
                break
        
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Add patient info to appointment
        appointment_data = appointment.copy()
        appointment_data['patient_id'] = patient.get('patient_id')
        appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
        appointment_data['patient_email'] = patient.get('email', '')
        appointment_data['patient_mobile'] = patient.get('mobile', '')
        
        print(f"[OK] Found appointment: {appointment_data}")
        
        return jsonify({
            "appointment": appointment_data,
            "message": "Appointment retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving doctor appointment: {str(e)}")
        return jsonify({"error": f"Failed to retrieve appointment: {str(e)}"}), 500


def update_doctor_appointment_service(appointment_id, data):
    """Update an existing appointment - EXACT from line 9333"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Doctor updating appointment {appointment_id} with data: {data}")
        
        # Find patient with this appointment
        patient = db.patients_collection.find_one({
            "appointments.appointment_id": appointment_id
        })
        if not patient:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Prepare update data - doctors can update all fields
        update_fields = {}
        allowed_fields = [
            'appointment_date', 'appointment_time', 'appointment_type', 
            'appointment_status', 'notes', 'patient_notes', 'doctor_notes', 'doctor_id'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields[f"appointments.$.{field}"] = data[field]
        
        if update_fields:
            update_fields["appointments.$.updated_at"] = datetime.now().isoformat()
            
            # Update the specific appointment in the array
            result = db.patients_collection.update_one(
                {"appointments.appointment_id": appointment_id},
                {"$set": update_fields}
            )
            
            if result.modified_count > 0:
                print(f"[OK] Appointment {appointment_id} updated successfully by doctor")
                return jsonify({"message": "Appointment updated successfully"}), 200
            else:
                return jsonify({"message": "No changes made"}), 200
        else:
            return jsonify({"message": "No valid fields to update"}), 400
        
    except Exception as e:
        print(f"[ERROR] Error updating doctor appointment: {str(e)}")
        return jsonify({"error": f"Failed to update appointment: {str(e)}"}), 500


def delete_doctor_appointment_service(appointment_id):
    """Delete an appointment - EXACT from line 9384"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Doctor deleting appointment {appointment_id}")
        
        # Find patient with this appointment
        patient = db.patients_collection.find_one({
            "appointments.appointment_id": appointment_id
        })
        if not patient:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Remove the appointment from the array
        result = db.patients_collection.update_one(
            {"appointments.appointment_id": appointment_id},
            {"$pull": {"appointments": {"appointment_id": appointment_id}}}
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment {appointment_id} deleted by doctor")
            return jsonify({"message": "Appointment deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete appointment"}), 500
        
    except Exception as e:
        print(f"[ERROR] Error deleting doctor appointment: {str(e)}")
        return jsonify({"error": f"Failed to delete appointment: {str(e)}"}), 500


def approve_appointment_service(appointment_id, data):
    """Approve a pending appointment - EXACT from line 9417"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        doctor_notes = data.get('doctor_notes', '')
        
        print(f"[*] Doctor approving appointment {appointment_id}")
        
        # Find patient with this appointment
        patient = db.patients_collection.find_one({
            "appointments.appointment_id": appointment_id
        })
        if not patient:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Update appointment status to approved
        result = db.patients_collection.update_one(
            {"appointments.appointment_id": appointment_id},
            {
                "$set": {
                    "appointments.$.appointment_status": "confirmed",
                    "appointments.$.updated_at": datetime.now().isoformat(),
                    "appointments.$.approved_by": "doctor",
                    "appointments.$.doctor_notes": doctor_notes
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment {appointment_id} approved by doctor")
            return jsonify({"message": "Appointment approved successfully"}), 200
        else:
            return jsonify({"error": "Failed to approve appointment"}), 500
        
    except Exception as e:
        print(f"[ERROR] Error approving appointment: {str(e)}")
        return jsonify({"error": f"Failed to approve appointment: {str(e)}"}), 500


def reject_appointment_service(appointment_id, data):
    """Reject a pending appointment - EXACT from line 9460"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        doctor_notes = data.get('doctor_notes', '')
        rejection_reason = data.get('rejection_reason', '')
        
        print(f"[*] Doctor rejecting appointment {appointment_id}")
        
        # Find patient with this appointment
        patient = db.patients_collection.find_one({
            "appointments.appointment_id": appointment_id
        })
        if not patient:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Update appointment status to rejected
        result = db.patients_collection.update_one(
            {"appointments.appointment_id": appointment_id},
            {
                "$set": {
                    "appointments.$.appointment_status": "rejected",
                    "appointments.$.updated_at": datetime.now().isoformat(),
                    "appointments.$.rejected_by": "doctor",
                    "appointments.$.doctor_notes": doctor_notes,
                    "appointments.$.rejection_reason": rejection_reason
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"[OK] Appointment {appointment_id} rejected by doctor")
            return jsonify({"message": "Appointment rejected successfully"}), 200
        else:
            return jsonify({"error": "Failed to reject appointment"}), 500
        
    except Exception as e:
        print(f"[ERROR] Error rejecting appointment: {str(e)}")
        return jsonify({"error": f"Failed to reject appointment: {str(e)}"}), 500


def get_pending_appointments_service():
    """Get all pending appointments for doctor approval - EXACT from line 9505"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting pending appointments for doctor")
        
        # Get all patients with pending appointments
        patients = db.patients_collection.find({
            "appointments.appointment_status": "pending"
        })
        
        pending_appointments = []
        for patient in patients:
            appointments = patient.get('appointments', [])
            for appointment in appointments:
                if appointment.get('appointment_status') == 'pending':
                    # Add patient info to appointment
                    appointment_data = appointment.copy()
                    appointment_data['patient_id'] = patient.get('patient_id')
                    appointment_data['patient_name'] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown')
                    appointment_data['patient_email'] = patient.get('email', '')
                    appointment_data['patient_mobile'] = patient.get('mobile', '')
                    
                    pending_appointments.append(appointment_data)
        
        # Sort by creation date (oldest first)
        pending_appointments.sort(key=lambda x: x.get('created_at', ''))
        
        print(f"[OK] Found {len(pending_appointments)} pending appointments")
        
        return jsonify({
            "pending_appointments": pending_appointments,
            "total_count": len(pending_appointments),
            "message": "Pending appointments retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving pending appointments: {str(e)}")
        return jsonify({"error": f"Failed to retrieve pending appointments: {str(e)}"}), 500


def get_appointment_statistics_service():
    """Get appointment statistics for doctor dashboard - EXACT from line 9549"""
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        print(f"[*] Getting appointment statistics for doctor")
        
        # Get all patients with appointments
        patients = db.patients_collection.find({})
        
        stats = {
            "total_appointments": 0,
            "pending": 0,
            "confirmed": 0,
            "cancelled": 0,
            "completed": 0,
            "rejected": 0,
            "today_appointments": 0,
            "upcoming_appointments": 0
        }
        
        today = datetime.now().date()
        
        for patient in patients:
            appointments = patient.get('appointments', [])
            for appointment in appointments:
                stats["total_appointments"] += 1
                
                status = appointment.get('appointment_status', '')
                if status in stats:
                    stats[status] += 1
                
                # Check if appointment is today
                appointment_date_str = appointment.get('appointment_date', '')
                try:
                    appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
                    if appointment_date == today:
                        stats["today_appointments"] += 1
                    elif appointment_date > today and status in ['scheduled', 'confirmed', 'pending']:
                        stats["upcoming_appointments"] += 1
                except ValueError:
                    continue
        
        print(f"[OK] Appointment statistics calculated: {stats}")
        
        return jsonify({
            "statistics": stats,
            "message": "Appointment statistics retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error retrieving appointment statistics: {str(e)}")
        return jsonify({"error": f"Failed to retrieve appointment statistics: {str(e)}"}), 500
