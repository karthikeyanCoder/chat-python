"""
Authentication Service - FUNCTION-BASED MVC
EXTRACTED FROM app_simple.py
Contains EXACT business logic, just reorganized - NO CHANGES to functionality

Architecture:
- Function-based services (each endpoint = one function)
- Database imported globally (db singleton pattern)
- Original logic preserved exactly

Note: This module uses function-based approach for backward compatibility.
Consider refactoring to class-based for consistency with other modules.
"""
import jwt
from datetime import datetime, timedelta
from flask import jsonify
from typing import Dict, Any, Tuple, Optional

from app.core.auth import generate_unique_patient_id, generate_jwt_token
from app.core.email import generate_otp, send_otp_email, send_patient_id_email
from app.core.validators import hash_password, verify_password, validate_email, validate_mobile, is_profile_complete
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.core.database import db


def capitalize_string_value(value):
    """Capitalize first letter of a string value"""
    if isinstance(value, str) and value:
        return value[0].upper() + value[1:] if len(value) > 1 else value.upper()
    return value


def capitalize_data_for_storage(data: Dict[str, Any], exclude_fields: list = None) -> Dict[str, Any]:
    """
    Capitalize first letter of string values in data dictionary before storing in database.
    Excludes specified fields like email, mobile, password, etc.
    
    Args:
        data: Dictionary containing data to be stored
        exclude_fields: List of field names to exclude from capitalization
        
    Returns:
        Dictionary with capitalized string values
    """
    if exclude_fields is None:
        exclude_fields = ['email', 'password', 'mobile', 'password_hash', 'patient_id', 
                         'otp', 'signup_token', 'login_identifier', 'emergency_contact_phone']
    
    capitalized_data = {}
    for key, value in data.items():
        if key in exclude_fields:
            capitalized_data[key] = value
        elif isinstance(value, str) and value:
            capitalized_data[key] = capitalize_string_value(value)
        elif isinstance(value, list):
            # Capitalize strings in lists (for medical_conditions, allergies, medications)
            capitalized_data[key] = [
                capitalize_string_value(v) if isinstance(v, str) and v else v 
                for v in value
            ]
        else:
            capitalized_data[key] = value
    
    return capitalized_data


# Error messages constants for consistency
class AuthErrorMessages:
    """Centralized error messages for authentication"""
    DB_NOT_CONNECTED = "Database not connected"
    MISSING_FIELD = "Missing required field: {field}"
    INVALID_EMAIL = "Invalid email format"
    INVALID_MOBILE = "Invalid mobile number"
    USERNAME_EXISTS = "Username already exists"
    EMAIL_EXISTS = "Email already exists and is active"
    MOBILE_EXISTS = "Mobile number already exists"
    INVALID_CREDENTIALS = "Invalid email or password"
    USER_NOT_FOUND = "User not found"
    ACCOUNT_INACTIVE = "Account is not active. Please verify OTP first."


def signup_service(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Register a new patient - Step 1: Collect data and send OTP (JWT-based)
    EXTRACTED FROM app_simple.py lines 1462-1537
    EXACT SAME LOGIC - NO CHANGES
    
    Args:
        data: Dictionary containing signup details
              Required: username, email, mobile, password
    
    Returns:
        Tuple of (response_dict, http_status_code)
    """
    try:
        # Check database connection and attempt reconnection if needed
        if not db.is_connected() or db.patients_collection is None:
            print("[WARN] Database not connected during signup, attempting reconnection...")
            if not db.reconnect():
                return jsonify({"error": "Database connection error - unable to connect. Please check your MONGO_URI and DB_NAME in .env file."}), 503
        
        # Validate required fields
        required_fields = ['username', 'email', 'mobile', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        username = capitalize_string_value(data['username'].strip())
        email = data['email'].strip()
        mobile = data['mobile'].strip()
        password = data['password']
        
        # Validate email and mobile
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        if not validate_mobile(mobile):
            return jsonify({"error": "Invalid mobile number"}), 400
        
        # Check if username exists
        if db.patients_collection.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400
        
        # Check if email exists and is already active
        existing_user = db.patients_collection.find_one({"email": email})
        if existing_user and existing_user.get("status") == "active":
            return jsonify({"error": "Email already exists and is active"}), 400
        
        # Check if mobile exists
        if db.patients_collection.find_one({"mobile": mobile}):
            return jsonify({"error": "Mobile number already exists"}), 400
        
        # Generate OTP
        otp = generate_otp()
        
        # Create JWT token with signup data (expires in 10 minutes)
        signup_payload = {
            "username": username,
            "email": email,
            "mobile": mobile,
            "password_hash": hash_password(password),
            "otp": otp,
            "exp": datetime.utcnow() + timedelta(minutes=10),
            "iat": datetime.utcnow(),
            "type": "signup_verification"
        }
        
        # Generate JWT token
        signup_token = jwt.encode(signup_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        # Send OTP email
        print(f"[*] Attempting to send OTP to: {email}")
        if send_otp_email(email, otp):
            return jsonify({
                "email": email,
                "status": "otp_sent",
                "message": "Please check your email for OTP verification.",
                "signup_token": signup_token  # Send token to frontend
            }), 200
        else:
            print(f"[ERROR] Failed to send OTP email to: {email}")
            return jsonify({
                "error": "Failed to send OTP email. Please check your email configuration.",
                "details": "Check console logs for more information"
            }), 500
    
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


def send_otp_service(data):
    """
    EXTRACTED FROM app_simple.py lines 1539-1582
    Send OTP to email for verification
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if user exists
        user = db.patients_collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in database (with expiration)
        db.patients_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "otp": otp,
                    "otp_created_at": datetime.now(),
                    "otp_expires_at": datetime.now() + timedelta(minutes=10)
                }
            }
        )
        
        # Send OTP email
        if send_otp_email(email, otp):
            return jsonify({
                "message": "OTP sent successfully",
                "email": email
            }), 200
        else:
            return jsonify({"error": "Failed to send OTP email"}), 500
    
    except Exception as e:
        return jsonify({"error": f"OTP sending failed: {str(e)}"}), 500


def resend_otp_service(data):
    """
    EXTRACTED FROM app_simple.py lines 1584-1635
    Resend OTP for signup verification (JWT-based)
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        email = data.get('email', '').strip()
        signup_token = data.get('signup_token', '').strip()
        
        if not email or not signup_token:
            return jsonify({"error": "Email and signup token are required"}), 400
        
        # Decode and verify JWT token
        try:
            payload = jwt.decode(signup_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Signup session has expired. Please start registration again."}), 400
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid signup token"}), 400
        
        # Verify token type and email match
        if payload.get("type") != "signup_verification":
            return jsonify({"error": "Invalid token type"}), 400
        
        if payload.get("email") != email:
            return jsonify({"error": "Email mismatch"}), 400
        
        # Generate new OTP
        new_otp = generate_otp()
        
        # Update JWT token with new OTP
        updated_payload = payload.copy()
        updated_payload["otp"] = new_otp
        updated_payload["exp"] = datetime.utcnow() + timedelta(minutes=10)  # Reset expiration
        
        # Generate new JWT token
        new_signup_token = jwt.encode(updated_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        # Send OTP email
        if send_otp_email(email, new_otp):
            return jsonify({
                "message": "OTP resent successfully",
                "email": email,
                "signup_token": new_signup_token
            }), 200
        else:
            return jsonify({"error": "Failed to send OTP email"}), 500
    
    except Exception as e:
        return jsonify({"error": f"OTP resend failed: {str(e)}"}), 500


def verify_otp_service(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    EXTRACTED FROM app_simple.py lines 1637-1743
    Verify OTP and create actual account (JWT-based)
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()
        signup_token = data.get('signup_token', '').strip()
        
        if not email or not otp or not signup_token:
            return jsonify({"error": "Email, OTP, and signup token are required"}), 400
        
        # Decode and verify JWT token
        try:
            payload = jwt.decode(signup_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Signup session has expired. Please start registration again."}), 400
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid signup token"}), 400
        
        # Verify token type and email match
        if payload.get("type") != "signup_verification":
            return jsonify({"error": "Invalid token type"}), 400
        
        if payload.get("email") != email:
            return jsonify({"error": "Email mismatch"}), 400
        
        # Check OTP
        if payload.get("otp") != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Extract user data from JWT payload
        username = payload.get("username")
        mobile = payload.get("mobile")
        password_hash = payload.get("password_hash")
        
        if not all([username, mobile, password_hash]):
            return jsonify({"error": "Invalid signup data in token"}), 400
        
        # Check if user already exists (handle duplicate key error)
        existing_user = db.patients_collection.find_one({"email": email})
        if existing_user:
            # User already exists, update their status to active and verify email
            db.patients_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "status": "active",
                        "email_verified": True,
                        "verified_at": datetime.now(),
                        "password_hash": password_hash,  # Update password
                        "username": username,  # Update username
                        "mobile": mobile  # Update mobile
                    }
                }
            )
            
            # Get the updated user data
            updated_user = db.patients_collection.find_one({"email": email})
            patient_id = updated_user.get("patient_id")
        else:
            # Generate unique patient ID for new account
            patient_id = generate_unique_patient_id()
            
            # Create new account in database
            user_data = {
                "patient_id": patient_id,
                "username": username,
                "email": email,
                "mobile": mobile,
                "password_hash": password_hash,
                "status": "active",
                "email_verified": True,
                "verified_at": datetime.now(),
                "created_at": datetime.now()
            }
            
            # Insert new user into database
            result = db.patients_collection.insert_one(user_data)
            
            if not result.inserted_id:
                return jsonify({"error": "Failed to create account"}), 500
            
            # Get the created user data
            updated_user = user_data
        
        # Send Patient ID email
        send_patient_id_email(email, patient_id, username)
        
        # Generate JWT token for login
        token = generate_jwt_token(updated_user)
        
        return jsonify({
            "patient_id": patient_id,
            "username": username,
            "email": email,
            "mobile": mobile,
            "status": "active",
            "token": token,
            "message": "Account created and verified successfully! Your Patient ID has been sent to your email."
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"OTP verification failed: {str(e)}"}), 500


def login_service(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    EXTRACTED FROM app_simple.py lines 1745-1828
    Login patient with Patient ID/Email and password
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        # Import activity tracker
        from app.shared.activity_tracker import UserActivityTracker
        activity_tracker = UserActivityTracker(db)
        
        # Check database connection and attempt reconnection if needed
        if not db.is_connected():
            print("[WARN] Database not connected during login, attempting reconnection...")
            if not db.reconnect():
                return jsonify({"error": "Database connection error - unable to reconnect"}), 503
        
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        login_identifier = data.get('login_identifier', '').strip()
        password = data.get('password', '')
        
        print(f"[DEBUG] Login attempt - identifier: {login_identifier[:10]}..., password provided: {bool(password)}")
        
        if not login_identifier or not password:
            print(f"[DEBUG] Login failed - missing fields: identifier={bool(login_identifier)}, password={bool(password)}")
            return jsonify({"error": "Login identifier and password are required"}), 400
        
        # Find user by Patient ID or Email
        print(f"[DEBUG] Searching for user by patient_id: {login_identifier}")
        user = db.patients_collection.find_one({"patient_id": login_identifier})
        if not user:
            print(f"[DEBUG] User not found by patient_id, searching by email: {login_identifier}")
            user = db.patients_collection.find_one({"email": login_identifier})
        
        if not user:
            print(f"[DEBUG] Login failed - User not found with identifier: {login_identifier}")
            return jsonify({"error": "Invalid credentials - User not found"}), 401
        
        print(f"[DEBUG] User found - patient_id: {user.get('patient_id')}, email: {user.get('email')}, status: {user.get('status')}")
        
        # Check if account is active
        if user.get("status") != "active":
            print(f"[DEBUG] Login failed - Account not active. Status: {user.get('status')}")
            return jsonify({"error": "Account not activated. Please verify your email."}), 401
        
        # Verify password
        print(f"[DEBUG] Verifying password...")
        password_valid = verify_password(password, user["password_hash"])
        if not password_valid:
            print(f"[DEBUG] Login failed - Password verification failed")
            return jsonify({"error": "Invalid credentials - Password incorrect"}), 401
        
        print(f"[DEBUG] Password verified successfully")
        
        # Check profile completion
        profile_complete = is_profile_complete(user)
        
        # Check if patient is connected to a doctor
        is_connected_to_doctor = False
        try:
            from app.modules.invite.repository import InviteRepository
            repo = InviteRepository(db)
            patient_connections = repo.get_patient_connections(user["patient_id"], "active")
            is_connected_to_doctor = len(patient_connections) > 0
        except Exception as e:
            print(f"[WARN] Could not check doctor connection status: {str(e)}")
            is_connected_to_doctor = False
        
        # Debug logging to identify null values
        print(f"[*] Login Debug - User Data:")
        print(f"  patient_id: {user.get('patient_id')}")
        print(f"  username: {user.get('username')}")
        print(f"  email: {user.get('email')}")
        print(f"  _id: {user.get('_id')}")
        print(f"  status: {user.get('status')}")
        print(f"  profile_complete: {profile_complete}")
        print(f"  is_connected_to_doctor: {is_connected_to_doctor}")
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        # Start tracking user session (only if activity tracker has collection)
        session_id = None
        if activity_tracker.activities_collection is not None:
            session_id = activity_tracker.start_user_session(
                user_email=user["email"],
                user_role="patient",
                username=user["username"],
                user_id=user["patient_id"]
            )
            
            # Log login activity
            activity_tracker.log_activity(
                user_email=user["email"],
                activity_type="login",
                activity_data={
                    "login_method": "email" if "@" in login_identifier else "patient_id",
                    "profile_complete": profile_complete,
                    "session_id": session_id
                },
                session_id=session_id
            )
        
        return jsonify({
            "email": user["email"],
            "is_profile_complete": profile_complete,
            "message": "Login successful",
            "object_id": str(user.get("_id")),
            "patient_id": user["patient_id"],
            "session_id": session_id,
            "token": token,
            "username": user.get("username", user.get("name", "User")),
            "user_data": {
                "patient_id": user["patient_id"],
                "email": user["email"],
                "username": user.get("username", user.get("name", "User")),
                "is_profile_complete": profile_complete,
                "is_connected_to_doctor": is_connected_to_doctor
            }
        }), 200
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


def logout_service(user_data):
    """
    EXTRACTED FROM app_simple.py lines 1830-1862
    User logout
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        from app.shared.activity_tracker import UserActivityTracker
        activity_tracker = UserActivityTracker(db)
        
        patient_id = user_data.get('patient_id')
        email = user_data.get('email')
        
        # End user session
        if email:
            activity_tracker.end_user_session(email)
            
            # Log logout activity
            activity_tracker.log_activity(
                user_email=email,
                activity_type="logout",
                activity_data={
                    "patient_id": patient_id,
                    "logout_time": datetime.now().isoformat()
                }
            )
        
        return jsonify({"message": "Logout successful"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500


def forgot_password_service(data):
    """
    EXTRACTED FROM app_simple.py lines 1864-1912
    Send password reset OTP
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if user exists
        user = db.patients_collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "Email not found"}), 404
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in database
        db.patients_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "reset_otp": otp,
                    "reset_otp_created_at": datetime.now(),
                    "reset_otp_expires_at": datetime.now() + timedelta(minutes=10)
                }
            }
        )
        
        # Send OTP email
        if send_otp_email(email, otp):
            return jsonify({
                "message": "Password reset OTP sent to your email",
                "email": email
            }), 200
        else:
            return jsonify({"error": "Failed to send OTP email"}), 500
    
    except Exception as e:
        return jsonify({"error": f"Password reset failed: {str(e)}"}), 500


def reset_password_service(data):
    """
    EXTRACTED FROM app_simple.py lines 1914-1971
    Reset password with OTP
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()
        new_password = data.get('new_password', '')
        
        if not email or not otp or not new_password:
            return jsonify({"error": "Email, OTP, and new password are required"}), 400
        
        # Find user
        user = db.patients_collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check OTP
        stored_otp = user.get("reset_otp")
        otp_expires_at = user.get("reset_otp_expires_at")
        
        if not stored_otp or stored_otp != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        if otp_expires_at and datetime.now() > otp_expires_at:
            return jsonify({"error": "OTP has expired"}), 400
        
        # Hash new password
        new_password_hash = hash_password(new_password)
        
        # Update password and clear OTP
        db.patients_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.now()
                },
                "$unset": {
                    "reset_otp": "",
                    "reset_otp_created_at": "",
                    "reset_otp_expires_at": ""
                }
            }
        )
        
        return jsonify({"message": "Password reset successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Password reset failed: {str(e)}"}), 500


def complete_profile_service(patient_id, data):
    """
    EXTRACTED FROM app_simple.py lines 1973-2073
    Complete patient profile
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        # Validate required fields (9 core fields)
        required_fields = [
            'first_name', 'last_name', 'date_of_birth', 'blood_type', 'gender',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'address', 'height', 'weight', 'is_pregnant', 'last_period_date'
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Calculate pregnancy data from LMP if pregnant
        pregnancy_week = None
        expected_delivery_date = None
        
        if data.get('is_pregnant') and data.get('last_period_date'):
            try:
                from datetime import datetime, timedelta
                lmp_date = datetime.strptime(data.get('last_period_date'), '%Y-%m-%d')
                today = datetime.now()
                
                # Calculate pregnancy week (assuming 40-week pregnancy)
                days_pregnant = (today - lmp_date).days
                pregnancy_week = min((days_pregnant // 7) + 1, 42)  # Cap at 42 weeks
                
                # Calculate expected delivery date (LMP + 280 days)
                expected_delivery_date = (lmp_date + timedelta(days=280)).strftime('%Y-%m-%d')
                
            except ValueError:
                return jsonify({"error": "Invalid last_period_date format. Use YYYY-MM-DD"}), 400
        
        # Extract profile data
        profile_data = {
            "first_name": data.get('first_name', '').strip(),
            "last_name": data.get('last_name', '').strip(),
            "date_of_birth": data.get('date_of_birth'),
            "blood_type": data.get('blood_type', '').strip(),
            "gender": data.get('gender', '').strip(),
            "emergency_contact_name": data.get('emergency_contact_name', '').strip(),
            "emergency_contact_phone": data.get('emergency_contact_phone', '').strip(),
            "emergency_contact_relationship": data.get('emergency_contact_relationship', '').strip(),
            "address": data.get('address', '').strip(),
            "height": data.get('height'),
            "weight": data.get('weight'),
            "is_pregnant": data.get('is_pregnant'),
            "last_period_date": data.get('last_period_date'),
            "pregnancy_week": pregnancy_week,  # Auto-calculated
            "expected_delivery_date": expected_delivery_date,  # Auto-calculated
            "medical_conditions": data.get('medical_conditions', []),
            "allergies": data.get('allergies', []),
            "current_medications": data.get('current_medications', []),
            "profile_completed": True,
            "profile_completed_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Capitalize string fields before storing (excluding IDs, dates, numbers, phone)
        exclude_fields = ['patient_id', 'date_of_birth', 'last_period_date', 'expected_delivery_date',
                         'height', 'weight', 'is_pregnant', 'pregnancy_week', 'emergency_contact_phone',
                         'profile_completed', 'profile_completed_at', 'updated_at']
        profile_data = capitalize_data_for_storage(profile_data, exclude_fields=exclude_fields)
        
        # Update patient profile
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": profile_data}
        )
        
        if result.modified_count > 0:
            return jsonify({
                "message": "Profile completed successfully",
                "patient_id": patient_id
            }), 200
        else:
            return jsonify({"error": "Failed to update profile. Patient ID not found or no changes made."}), 400
    
    except Exception as e:
        return jsonify({"error": f"Profile completion failed: {str(e)}"}), 500


def edit_profile_service(data):
    """
    EXTRACTED FROM app_simple.py lines 2075-2167
    Edit/Update patient profile
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({"error": "Patient ID is required"}), 400
        
        # Build update data from request (only include fields that are provided)
        update_data = {}
        
        # Profile fields that can be updated
        updatable_fields = [
            'first_name', 'last_name', 'mobile', 'address', 'emergency_contact',
            'height', 'weight', 'medical_conditions', 'allergies', 'current_medications',
            'blood_type', 'gender'
        ]
        
        for field in updatable_fields:
            if field in data:
                # Strip strings if they are strings
                if isinstance(data[field], str):
                    update_data[field] = data[field].strip()
                else:
                    update_data[field] = data[field]
        
        # Add timestamp
        update_data['updated_at'] = datetime.now()
        
        # Capitalize string fields before storing (excluding patient_id, mobile, height, weight, dates)
        exclude_fields = ['patient_id', 'mobile', 'height', 'weight', 'updated_at']
        update_data = capitalize_data_for_storage(update_data, exclude_fields=exclude_fields)
        
        # Update patient profile
        result = db.patients_collection.update_one(
            {"patient_id": patient_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({"message": "Profile updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update profile. Patient ID not found or no changes made."}), 400
    
    except Exception as e:
        return jsonify({"error": f"Profile update failed: {str(e)}"}), 500


def verify_token_service(token):
    """
    EXTRACTED FROM app_simple.py lines 2169-2239
    Verify JWT token validity
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if not token:
            return jsonify({"error": "Token is required"}), 400
        
        # Verify token
        from app.core.auth import verify_jwt_token
        payload = verify_jwt_token(token)
        
        if payload:
            return jsonify({
                "valid": True,
                "patient_id": payload.get('patient_id'),
                "email": payload.get('email'),
                "username": payload.get('username'),
                "message": "Token is valid"
            }), 200
        else:
            return jsonify({
                "valid": False,
                "message": "Invalid or expired token"
            }), 401
    
    except Exception as e:
        return jsonify({"error": f"Token verification failed: {str(e)}"}), 500


def get_profile_service(patient_id: str) -> Tuple[Dict[str, Any], int]:
    """
    EXTRACTED FROM app_simple.py lines 2241-2316
    Get patient profile by ID
    EXACT SAME LOGIC - NO CHANGES
    """
    try:
        if db.patients_collection is None:
            return jsonify({"error": "Database not connected"}), 500
        
        # Find patient by ID
        patient = db.patients_collection.find_one({"patient_id": patient_id})
        
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Remove sensitive data
        if "_id" in patient:
            patient["_id"] = str(patient["_id"])
        
        # Remove password_hash from response
        if "password_hash" in patient:
            del patient["password_hash"]
        
        # Remove OTPs if present
        fields_to_remove = ['otp', 'reset_otp', 'otp_expires_at', 'reset_otp_expires_at']
        for field in fields_to_remove:
            if field in patient:
                del patient[field]
        
        return jsonify(patient), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve profile: {str(e)}"}), 500
