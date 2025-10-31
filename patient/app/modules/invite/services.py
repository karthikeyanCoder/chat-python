"""
Invite Module Services - Function-Based MVC
Handles doctor-patient invites and connections
EXTRACTED FROM patient_service/ - ZERO BACKEND LOGIC CHANGES
"""
from flask import jsonify
from datetime import datetime
from typing import Dict, Any, Tuple
from app.core.database import db
from app.core.email import send_email
from .repository import InviteRepository


def accept_invite_service(patient_id: str, patient_email: str, invite_code: str) -> Tuple[Dict, int]:
    """Patient accepts doctor's invite - EXACT from patient_service/controllers/connection_controller.py"""
    try:
        repo = InviteRepository(db)
        
        # Validate invite code
        is_valid, message, invite = repo.validate_invite_code(invite_code, patient_email)
        
        if not is_valid:
            return jsonify({"success": False, "error": message}), 400
        
        # Check if connection already exists
        if repo.connection_exists(invite['doctor_id'], patient_id):
            return jsonify({
                "success": False,
                "error": "Connection already exists with this doctor"
            }), 400
        
        # Create connection
        connection = repo.create_connection(
            doctor_id=invite['doctor_id'],
            patient_id=patient_id,
            invited_by="doctor",
            invite_code=invite_code,
            connection_type="primary"
        )
        
        # Mark invite as used
        repo.mark_invite_as_used(invite_code)
        
        # Update doctor statistics
        repo.increment_doctor_patient_count(invite['doctor_id'])
        
        # Get doctor info
        doctor = repo.find_doctor_by_id(invite['doctor_id'])
        
        print(f"[OK] Patient {patient_id} accepted invite from doctor {invite['doctor_id']}")
        
        # Support both flat and nested doctor structures
        if doctor:
            doctor_name = (doctor.get('personal_info', {}).get('full_name') or 
                          doctor.get('name', 'Unknown Doctor'))
            doctor_specialty = (doctor.get('professional_info', {}).get('specialty') or 
                               doctor.get('specialty', 'General Medicine'))
            doctor_hospital = (doctor.get('workplace_info', {}).get('hospital_name') or 
                              doctor.get('location', 'Not specified'))
        
        return jsonify({
            "success": True,
            "message": f"Successfully connected with {doctor_name}" if doctor else "Successfully connected",
            "connection": {
                "connection_id": connection['connection_id'],
                "status": connection['status'],
                "connected_at": connection['dates']['connected_at'].isoformat()
            },
            "doctor": {
                "doctor_id": doctor['doctor_id'],
                "name": doctor_name,
                "specialty": doctor_specialty,
                "hospital": doctor_hospital
            } if doctor else None
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Accept invite failed: {e}")
        return jsonify({"success": False, "error": f"Failed to accept invite: {str(e)}"}), 500


def request_connection_service(patient_id: str, message: str, 
                               connection_type: str = "primary", 
                               doctor_id: str = None, doctor_email: str = None,
                               send_invite_code: bool = True,
                               expires_in_days: int = 7) -> Tuple[Dict, int]:
    """Patient requests connection with doctor using either doctor_id or doctor_email"""
    try:
        repo = InviteRepository(db)
        
        # Find doctor by either ID or email
        doctor = None
        if doctor_id:
            doctor = repo.find_doctor_by_id(doctor_id)
            if not doctor:
                return jsonify({"success": False, "error": "Doctor not found with provided ID"}), 404
        elif doctor_email:
            doctor = repo.find_doctor_by_email(doctor_email)
            if not doctor:
                return jsonify({"success": False, "error": "Doctor not found with provided email"}), 404
            # Get doctor_id from found doctor
            doctor_id = doctor.get('doctor_id')
            if not doctor_id:
                return jsonify({"success": False, "error": "Doctor record missing ID"}), 404
        
        # Check if connection already exists
        if repo.connection_exists(doctor_id, patient_id):
            return jsonify({
                "success": False,
                "error": "Connection request already exists with this doctor"
            }), 400
        
        # Generate invite code if requested
        invite_code = None
        invite_data = None
        if send_invite_code:
            from .helpers import InviteHelpers
            invite_data = InviteHelpers.create_invite_data(
                doctor_id=doctor_id,
                patient_email=doctor.get('personal_info', {}).get('email') or doctor.get('email', ''),
                expires_in_days=expires_in_days,
                message=message
            )
            invite_code = invite_data['invite_code']
            
            # Store invite code in database
            try:
                db.invite_codes_collection.insert_one(invite_data)
                print(f"[OK] Stored invite code {invite_code} for doctor {doctor_id}")
            except Exception as e:
                print(f"[WARNING] Failed to store invite code: {e}")
                # Continue without failing the request
        
        # Create pending connection
        connection = repo.create_connection(
            doctor_id=doctor_id,
            patient_id=patient_id,
            invited_by="patient",
            request_message=message,
            connection_type=connection_type,
            invite_code=invite_code
        )
        
        print(f"[OK] Patient {patient_id} requested connection with doctor {doctor_id}")
        
        # Support both flat and nested doctor structures
        doctor_name = (doctor.get('personal_info', {}).get('full_name') or 
                      doctor.get('name', 'Unknown Doctor'))
        doctor_specialty = (doctor.get('professional_info', {}).get('specialty') or 
                           doctor.get('specialty', 'General Medicine'))
        
        # Get patient information for email
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        patient_name = "Unknown Patient"
        patient_email = "unknown@example.com"
        
        if patient:
            patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or patient.get('username', 'Unknown Patient')
            patient_email = patient.get('email', 'unknown@example.com')
        
        # Send email notification to doctor
        email_status = False  # Initialize as False
        
        try:
            # Get doctor's email address
            doctor_email_address = (doctor.get('personal_info', {}).get('email') or 
                                  doctor.get('email', ''))
            
            if doctor_email_address:
                # Prepare email content
                subject = f"New Patient Connection Request - {patient_name}"
                
                # Base email body
                email_body = f"""
Dear Dr. {doctor_name},

You have received a new patient connection request:

Patient Details:
- Name: {patient_name}
- Email: {patient_email}
- Connection Type: {connection_type.title()}
- Request Message: {message}

Connection Details:
- Connection ID: {connection['connection_id']}
- Requested At: {connection['dates']['request_sent_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}
- Status: Pending
"""
                
                # Add invite code section if available
                if invite_code and invite_data:
                    email_body += f"""
Invite Code Details:
- Invite Code: {invite_code}
- Expires: {invite_data['expires_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}
- Usage Limit: {invite_data['usage_limit']} time(s)

You can use this invite code to quickly accept the connection request.
"""
                
                email_body += """
Please log into your doctor dashboard to review and respond to this connection request.

Best regards,
Patient Alert System
                """
                
                # Send email to doctor
                email_sent = send_email(
                    to_email=doctor_email_address,
                    subject=subject,
                    body=email_body
                )
                
                if email_sent:
                    print(f"[OK] Email notification sent to doctor {doctor_email_address}")
                    email_status = True
                else:
                    print(f"[WARNING] Failed to send email notification to doctor {doctor_email_address}")
                    email_status = False
            else:
                print(f"[WARNING] Doctor {doctor_id} has no email address for notification")
                email_status = False
                
        except Exception as email_error:
            print(f"[WARNING] Email notification failed: {email_error}")
            email_status = False
            # Don't fail the entire request if email fails
        
        response_data = {
            "success": True,
            "message": f"Connection request sent to {doctor_name}",
            "request": {
                "request_id": connection['connection_id'],
                "connection_id": connection['connection_id'],
                "status": "pending",
                "requested_at": connection['dates']['request_sent_at'].isoformat(),
                "estimated_response_time": "24-48 hours"
            },
            "doctor": {
                "doctor_id": doctor_id,
                "name": doctor_name,
                "specialty": doctor_specialty
            },
            "email_sent": email_status
        }
        
        # Add invite code information if available
        if invite_code and invite_data:
            response_data["invite_code"] = {
                "code": invite_code,
                "expires_at": invite_data['expires_at'].isoformat(),
                "usage_limit": invite_data['usage_limit'],
                "status": "active"
            }
            response_data["message"] += f" with invite code {invite_code}"
        
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"[ERROR] Request connection failed: {e}")
        return jsonify({"success": False, "error": f"Failed to send request: {str(e)}"}), 500


def remove_connection_service(connection_id: str, patient_id: str, reason: str = None) -> Tuple[Dict, int]:
    """Remove connection from patient side - EXACT from patient_service/controllers/connection_controller.py"""
    try:
        repo = InviteRepository(db)
        
        # Get connection
        connection = repo.find_connection_by_id(connection_id)
        
        if not connection:
            return jsonify({"success": False, "error": "Connection not found"}), 404
        
        # Verify patient owns this connection
        if connection['patient_id'] != patient_id:
            return jsonify({"success": False, "error": "Not your connection"}), 403
        
        # Remove connection
        success = repo.remove_connection(connection_id, patient_id, "patient", reason)
        
        if not success:
            return jsonify({"success": False, "error": "Failed to remove connection"}), 500
        
        # Update doctor statistics if connection was active
        if connection['status'] == 'active':
            repo.decrement_doctor_patient_count(connection['doctor_id'])
        
        print(f"[OK] Patient {patient_id} removed connection {connection_id}")
        
        return jsonify({
            "success": True,
            "message": "Connection removed successfully",
            "connection": {
                "connection_id": connection_id,
                "status": "removed"
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Remove connection failed: {e}")
        return jsonify({"success": False, "error": f"Failed to remove connection: {str(e)}"}), 500


def get_connected_doctors_service(patient_id: str) -> Tuple[Dict, int]:
    """Get all connected doctors for a patient - EXACT from patient_service/controllers/patient_controller.py"""
    try:
        repo = InviteRepository(db)
        
        # Get active connections
        connections = repo.get_patient_connections(patient_id, "active")
        
        # Enrich with doctor details
        doctors = []
        for conn in connections:
            doctor = repo.find_doctor_by_id(conn['doctor_id'])
            if not doctor:
                continue
            
            # Support both flat and nested doctor structures
            name = (doctor.get('personal_info', {}).get('full_name') or 
                   doctor.get('name', 'Unknown Doctor'))
            specialty = (doctor.get('professional_info', {}).get('specialty') or 
                        doctor.get('specialty', 'General Medicine'))
            hospital = (doctor.get('workplace_info', {}).get('hospital_name') or 
                       doctor.get('location', 'Not specified'))
            profile_photo = (doctor.get('personal_info', {}).get('profile_photo') or 
                           doctor.get('profile_image', ''))
            experience = (doctor.get('professional_info', {}).get('years_of_experience') or 
                         doctor.get('experience', 0))
            rating = (doctor.get('ratings', {}).get('average_rating') or 
                     doctor.get('rating', 0))
            
            doctors.append({
                "connection_id": conn['connection_id'],
                "doctor_id": doctor['doctor_id'],
                "name": name,
                "specialty": specialty,
                "hospital": hospital,
                "profile_photo": profile_photo,
                "years_experience": experience,
                "rating": rating,
                "connection_info": {
                    "connected_since": conn['dates']['connected_at'].isoformat() if conn['dates'].get('connected_at') else None,
                    "is_primary": conn['connection_type'] == 'primary',
                    "connection_type": conn['connection_type'],
                    "status": conn['status']
                }
            })
        
        print(f"[OK] Found {len(doctors)} connected doctors for patient {patient_id}")
        
        return jsonify({
            "success": True,
            "doctors": doctors,
            "total_count": len(doctors)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get connected doctors failed: {e}")
        return jsonify({"success": False, "error": f"Failed to fetch doctors: {str(e)}"}), 500


def search_doctors_service(patient_id: str, query: str = None, specialty: str = None,
                           city: str = None, limit: int = 20) -> Tuple[Dict, int]:
    """Search for doctors with connection status - EXACT from patient_service/controllers/patient_controller.py"""
    try:
        repo = InviteRepository(db)
        
        # Search doctors
        doctors = repo.search_doctors(query, specialty, city, limit)
        
        # Check connection status for each doctor
        results = []
        for doctor in doctors:
            connection = repo.find_connection(doctor['doctor_id'], patient_id)
            
            # Support both flat and nested doctor structures
            name = (doctor.get('personal_info', {}).get('full_name') or 
                   doctor.get('name', 'Unknown Doctor'))
            specialty = (doctor.get('professional_info', {}).get('specialty') or 
                        doctor.get('specialty', 'General Medicine'))
            hospital = (doctor.get('workplace_info', {}).get('hospital_name') or 
                       doctor.get('location', 'Not specified'))
            city = (doctor.get('workplace_info', {}).get('hospital_address', {}).get('city') or 
                   doctor.get('city', 'Unknown'))
            state = (doctor.get('workplace_info', {}).get('hospital_address', {}).get('state') or 
                    doctor.get('state', ''))
            experience = (doctor.get('professional_info', {}).get('years_of_experience') or 
                         doctor.get('experience', 0))
            rating = (doctor.get('ratings', {}).get('average_rating') or 
                     doctor.get('rating', 0))
            profile_photo = (doctor.get('personal_info', {}).get('profile_photo') or 
                           doctor.get('profile_image', ''))
            
            results.append({
                "doctor_id": doctor['doctor_id'],
                "name": name,
                "specialty": specialty,
                "hospital": hospital,
                "location": {
                    "city": city,
                    "state": state
                },
                "years_experience": experience,
                "rating": rating,
                "profile_photo": profile_photo,
                "is_connected": bool(connection),
                "connection_status": connection['status'] if connection else 'none'
            })
        
        print(f"[OK] Found {len(results)} doctors matching search criteria")
        
        return jsonify({
            "success": True,
            "doctors": results,
            "total_count": len(results)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Search doctors failed: {e}")
        return jsonify({"success": False, "error": f"Search failed: {str(e)}"}), 500


def cancel_request_service(connection_id: str, patient_id: str, reason: str = None) -> Tuple[Dict, int]:
    """Cancel pending connection request from patient side"""
    try:
        repo = InviteRepository(db)
        
        # Get connection
        connection = repo.find_connection_by_id(connection_id)
        
        if not connection:
            return jsonify({"success": False, "error": "Connection request not found"}), 404
        
        # Verify patient owns this connection
        if connection['patient_id'] != patient_id:
            return jsonify({"success": False, "error": "Not your connection request"}), 403
        
        # Check if request is pending
        if connection['status'] != 'pending':
            return jsonify({
                "success": False, 
                "error": f"Cannot cancel request with status: {connection['status']}"
            }), 400
        
        # Cancel the request
        success = repo.cancel_request(connection_id, patient_id, "patient", reason)
        
        if not success:
            return jsonify({"success": False, "error": "Failed to cancel request"}), 500
        
        print(f"[OK] Patient {patient_id} cancelled connection request {connection_id}")
        
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
        print(f"[ERROR] Cancel request failed: {e}")
        return jsonify({"success": False, "error": f"Failed to cancel request: {str(e)}"}), 500


def get_pending_invites_service(patient_id: str) -> Tuple[Dict, int]:
    """Get pending connection requests from doctors for patient"""
    try:
        repo = InviteRepository(db)
        
        # Get pending invites from doctors
        invites = repo.get_patient_pending_invites(patient_id)
        
        # Format response with doctor details
        formatted_invites = []
        for invite in invites:
            doctor = repo.find_doctor_by_id(invite['doctor_id'])
            doctor_name = (doctor.get('personal_info', {}).get('full_name') or 
                          doctor.get('name', 'Unknown Doctor')) if doctor else 'Unknown Doctor'
            doctor_specialty = (doctor.get('professional_info', {}).get('specialty') or 
                               doctor.get('specialty', 'General Medicine')) if doctor else 'General Medicine'
            doctor_hospital = (doctor.get('professional_info', {}).get('hospital') or 
                              doctor.get('hospital', 'Unknown Hospital')) if doctor else 'Unknown Hospital'
            
            formatted_invites.append({
                "invite_id": invite['connection_id'],
                "doctor_id": invite['doctor_id'],
                "doctor_name": doctor_name,
                "doctor_specialty": doctor_specialty,
                "doctor_hospital": doctor_hospital,
                "invite_code": invite.get('invite_code'),
                "connection_type": invite.get('connection_type', 'primary'),
                "invited_at": invite['dates']['invite_sent_at'].isoformat() if invite['dates'].get('invite_sent_at') else None,
                "status": invite['status']
            })
        
        return jsonify({
            "success": True,
            "pending_invites": formatted_invites,
            "total_count": len(formatted_invites),
            "message": "Pending invites retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get pending invites failed: {e}")
        return jsonify({"success": False, "error": f"Failed to get pending invites: {str(e)}"}), 500


def get_invite_details_service(invite_id: str, patient_id: str) -> Tuple[Dict, int]:
    """Get details of a specific doctor invite"""
    try:
        repo = InviteRepository(db)
        
        # Get invite details
        invite = repo.get_patient_invite_details(invite_id, patient_id)
        if not invite:
            return jsonify({"success": False, "error": "Invite not found"}), 404
        
        # Get doctor details
        doctor = repo.find_doctor_by_id(invite['doctor_id'])
        doctor_name = (doctor.get('personal_info', {}).get('full_name') or 
                      doctor.get('name', 'Unknown Doctor')) if doctor else 'Unknown Doctor'
        doctor_specialty = (doctor.get('professional_info', {}).get('specialty') or 
                           doctor.get('specialty', 'General Medicine')) if doctor else 'General Medicine'
        doctor_hospital = (doctor.get('professional_info', {}).get('hospital') or 
                          doctor.get('hospital', 'Unknown Hospital')) if doctor else 'Unknown Hospital'
        
        return jsonify({
            "success": True,
            "invite": {
                "invite_id": invite['connection_id'],
                "doctor_id": invite['doctor_id'],
                "doctor_name": doctor_name,
                "doctor_specialty": doctor_specialty,
                "doctor_hospital": doctor_hospital,
                "invite_code": invite.get('invite_code'),
                "connection_type": invite.get('connection_type', 'primary'),
                "invited_at": invite['dates']['invite_sent_at'].isoformat() if invite['dates'].get('invite_sent_at') else None,
                "status": invite['status'],
                "permissions": invite.get('permissions', {}),
                "message": invite.get('request_message', '')
            },
            "message": "Invite details retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get invite details failed: {e}")
        return jsonify({"success": False, "error": f"Failed to get invite details: {str(e)}"}), 500


def verify_invite_code_service(invite_code: str) -> Tuple[Dict, int]:
    """Verify invite code - Public service (no auth required)"""
    try:
        repo = InviteRepository(db)
        
        # Validate format first
        if not repo.validate_invite_code_format(invite_code):
            return jsonify({
                "success": False,
                "valid": False,
                "error": "Invalid invite code format"
            }), 400
        
        # Find invite
        invite = repo.find_invite_by_code(invite_code)
        
        if not invite:
            repo._increment_invite_attempts(invite_code)
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invalid invite code"
            }), 404
        
        # Check status
        if invite['status'] != 'active':
            return jsonify({
                "success": False,
                "valid": False,
                "message": f"Invite code is {invite['status']}"
            }), 400
        
        # Check expiration
        if datetime.utcnow() > invite['expires_at']:
            repo.invite_codes_collection.update_one(
                {"invite_code": invite_code},
                {"$set": {"status": "expired", "updated_at": datetime.utcnow()}}
            )
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invite code has expired"
            }), 400
        
        # Check usage
        if invite['usage_count'] >= invite['usage_limit']:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invite code has been used"
            }), 400
        
        # Check security attempts
        if invite['security']['attempts_count'] >= invite['security']['max_attempts']:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Invite code locked due to too many attempts"
            }), 400
        
        return jsonify({
            "success": True,
            "valid": True,
            "message": "Valid invite code",
            "doctor": invite['doctor_info'],
            "invite_info": {
                "expires_at": invite['expires_at'].isoformat(),
                "remaining_uses": invite['usage_limit'] - invite['usage_count'],
                "custom_message": invite.get('custom_message', '')
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error verifying invite: {e}")
        return jsonify({
            "success": False,
            "valid": False,
            "error": f"Verification failed: {str(e)}"
        }), 500


