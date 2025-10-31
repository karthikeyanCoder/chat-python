"""
Auth Controller - Handles authentication operations
"""

from flask import jsonify
from typing import Dict, Any

class AuthController:
    """Authentication controller"""
    
    def __init__(self, doctor_model, patient_model, nurse_model, otp_model, jwt_service, email_service, validators):
        self.doctor_model = doctor_model
        self.patient_model = patient_model
        self.nurse_model = nurse_model
        self.otp_model = otp_model
        self.jwt_service = jwt_service
        self.email_service = email_service
        self.validators = validators
    
    def doctor_signup(self, request) -> tuple:
        """Doctor signup endpoint - automatically sends OTP"""
        try:
            data = request.get_json()
            
            # Extract doctor signup data
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            mobile = data.get('mobile', '').strip()
            password = data.get('password', '')
            role = data.get('role', 'doctor')
            
            # Validate required fields
            if not all([username, email, mobile, password]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Validate email and mobile
            if not self.validators.validate_email(email):
                return jsonify({"error": "Invalid email format"}), 400
            
            if not self.validators.validate_mobile(mobile):
                return jsonify({"error": "Invalid mobile number"}), 400
            
            # Check if email already exists
            if self.doctor_model.check_email_exists(email):
                return jsonify({'error': 'Email already exists'}), 400
            
            # Check if username already exists
            if self.doctor_model.check_username_exists(username):
                return jsonify({'error': 'Username already exists'}), 400
            
            # Check if mobile already exists
            if self.doctor_model.check_mobile_exists(mobile):
                return jsonify({'error': 'Mobile number already exists'}), 400
            
            # Prepare signup data for JWT
            signup_data = {
                'username': username,
                'email': email,
                'mobile': mobile,
                'password': password,
                'role': role,
            }
            
            # Store signup data temporarily for resend OTP functionality
            temp_result = self.otp_model.store_temp_signup_data(email, signup_data)
            if not temp_result['success']:
                return jsonify({'error': temp_result['error']}), 500
            
            print(f"💾 Stored temporary signup data for email: {email}")
            
            # AUTOMATICALLY GENERATE AND SEND OTP
            try:
                otp, jwt_token = self.jwt_service.generate_otp_jwt(email, 'doctor_signup', signup_data)
                print(f"🔐 Generated JWT OTP: {otp} for email: {email}")
                print(f"🔐 JWT Token: {jwt_token[:50]}...")
            except Exception as e:
                return jsonify({
                    "error": f"Failed to generate OTP: {str(e)}"
                }), 500
            
            # Send OTP email
            email_result = self.email_service.send_otp_email(email, otp)
            
            # Return the EXACT format you requested
            if email_result['success']:
                print(f"✅ OTP sent successfully to: {email}")
                return jsonify({
                    "email": email,
                    "message": "Please check your email for OTP verification.",
                    "signup_token": jwt_token,
                    "status": "otp_sent"
                }), 200
            else:
                # Email failed but OTP is available - return OTP anyway
                print(f"⚠️ Email sending failed, but OTP is available: {otp}")
                return jsonify({
                    "email": email,
                    "message": "Please check your email for OTP verification.",
                    "signup_token": jwt_token,
                    "status": "otp_sent"
                }), 200
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def patient_signup(self, request) -> tuple:
        """Patient signup endpoint"""
        try:
            data = request.get_json()
            
            # Extract patient signup data
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            mobile = data.get('mobile', '').strip()
            password = data.get('password', '')
            role = data.get('role', 'patient')
            
            # Validate required fields
            if not all([username, email, mobile, password]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Validate email and mobile
            if not self.validators.validate_email(email):
                return jsonify({"error": "Invalid email format"}), 400
            
            if not self.validators.validate_mobile(mobile):
                return jsonify({"error": "Invalid mobile number"}), 400
            
            # Check if email already exists
            if self.patient_model.check_email_exists(email):
                return jsonify({'error': 'Email already exists'}), 400
            
            # Check if username already exists
            if self.patient_model.check_username_exists(username):
                return jsonify({'error': 'Username already exists'}), 400
            
            # Check if mobile already exists
            if self.patient_model.check_mobile_exists(mobile):
                return jsonify({'error': 'Mobile number already exists'}), 400
            
            # Create patient
            result = self.patient_model.create_patient({
                'username': username,
                'email': email,
                'mobile': mobile,
                'password': password,
                'role': role
            })
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Patient created successfully',
                    'patient_id': result['patient_id']
                }), 200
            else:
                return jsonify({'error': result['error']}), 500
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def login(self, request) -> tuple:
        """Login endpoint for doctors, nurses and patients"""
        try:
            data = request.get_json()
            print(f"🔐 Login attempt with data: {data}")
            
            # Extract login data
            email = data.get('email', '').strip()
            password = data.get('password', '')
            role = data.get('role', 'doctor')  # Default to doctor role
            
            print(f"📧 Attempting login for email: {email}")
            
            # Validate required fields
            if not all([email, password]):
                print("❌ Missing email or password")
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Validate email format only if it looks like an email
            if '@' in email and not self.validators.validate_email(email):
                return jsonify({"error": "Invalid email format"}), 400
            
            # First try doctor login for both doctors and nurses
            if role in ['doctor', 'nurse']:
                return self._handle_doctor_login(email, password)
            else:  # patient role
                return self._handle_patient_login(email, password)
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
            
    def _handle_doctor_login(self, email, password):
        """Handle both doctor and nurse login logic"""
        try:
            print("\n🔐 Starting login process...")
            print(f"👤 Attempting to authenticate: {email}")
            
            # First try as doctor
            doctor = None
            if '@' in email:
                doctor = self.doctor_model.get_doctor_by_email(email)
                print(f"🔍 Looking up doctor by email: {email}")
                print(f"🔍 Doctor lookup result: {'Found' if doctor else 'Not found'}")
            else:
                doctor = self.doctor_model.get_doctor_by_id(email)
                print(f"🔍 Looking up doctor by ID: {email}")
                print(f"🔍 Doctor lookup result: {'Found' if doctor else 'Not found'}")

            # If doctor exists and password is correct, handle doctor login
            if doctor and self.doctor_model.verify_password(email, password):
                print(f"✅ Doctor authenticated: {doctor.get('email')}")
                
                # Generate JWT token for doctor
                token_data = {
                    'user_id': doctor.get('doctor_id', ''),
                    'email': doctor.get('email', ''),
                    'username': doctor.get('username', ''),
                    'role': 'doctor'
                }
                token = self.jwt_service.generate_token(token_data)
                
                # Check if profile is complete
                is_profile_complete = doctor.get('is_profile_complete', False)
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'doctor_id': doctor.get('doctor_id', ''),
                    'email': doctor.get('email', ''),
                    'username': doctor.get('username', ''),
                    'is_profile_complete': is_profile_complete,
                    'user': {
                        'id': doctor.get('doctor_id', ''),
                        'email': doctor.get('email', ''),
                        'username': doctor.get('username', ''),
                        'role': 'doctor'
                    }
                }), 200
            
            # If not a doctor or wrong password, try as nurse
            print("\n👩‍⚕️ Not a doctor or invalid doctor credentials, trying nurse...")
            print(f"🔍 Attempting nurse verification for email: {email}")
            
            # First verify if the nurse exists and password is correct
            if self.nurse_model.verify_password(email, password):
                print("✅ Nurse password verified successfully")
                # Get nurse details
                nurse_doc = self.nurse_model.find_by_email(email)
                if nurse_doc:
                    print(f"✅ Found nurse details: {nurse_doc['email']}")
                    nurse_result = {
                        'success': True,
                        'nurse_id': nurse_doc['nurse_id']
                    }
                else:
                    print("❌ Could not find nurse details after password verification")
                    return jsonify({'error': 'Failed to retrieve nurse details'}), 500
            else:
                print("❌ Nurse password verification failed")
                return jsonify({'error': 'Invalid credentials'}), 401

            if nurse_result['success']:
                print("🔄 Getting full nurse details...")
                # Found a nurse, get their details
                nurse_details = self.nurse_model.get_nurse_by_id(nurse_result['nurse_id'])
                if not nurse_details['success']:
                    print("❌ Failed to get nurse details")
                    return jsonify({'error': 'Failed to retrieve nurse details'}), 500
                
                nurse_data = nurse_details['data']
                print(f"Found nurse: {nurse_data['email']}")
                
                # Generate JWT token for nurse
                token_data = {
                    'user_id': nurse_data['nurse_id'],
                    'email': nurse_data['email'],
                    'doctor_id': nurse_data['doctor_id'],
                    'role': 'nurse'
                }
                token = self.jwt_service.generate_token(token_data)
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'nurse_id': nurse_data['nurse_id'],
                    'email': nurse_data['email'],
                    'doctor_id': nurse_data['doctor_id'],
                    'user': {
                        'id': nurse_data['nurse_id'],
                        'email': nurse_data['email'],
                        'role': 'nurse',
                        'doctor_id': nurse_data['doctor_id']
                    }
                }), 200
                
            # If we get here, neither doctor nor nurse credentials were valid
            return jsonify({'error': 'Invalid credentials'}), 401
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500

    def _handle_nurse_login(self, email, password):
        """Handle nurse login logic"""
        # Find nurse by email
        nurse = self.nurse_model.verify_nurse_password(email, password)
        
        if not nurse['success']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get nurse details
        nurse_details = self.nurse_model.get_nurse_by_id(nurse['nurse_id'])
        if not nurse_details['success']:
            return jsonify({'error': 'Failed to retrieve nurse details'}), 500
        
        nurse_data = nurse_details['data']
        
        # Generate JWT token
        token_data = {
            'user_id': nurse_data['nurse_id'],
            'email': nurse_data['email'],
            'doctor_id': nurse_data['doctor_id'],  # Include doctor_id for reference
            'role': 'nurse'
        }
        token = self.jwt_service.generate_token(token_data)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'nurse_id': nurse_data['nurse_id'],
            'email': nurse_data['email'],
            'doctor_id': nurse_data['doctor_id'],
            'user': {
                'id': nurse_data['nurse_id'],
                'email': nurse_data['email'],
                'role': 'nurse',
                'doctor_id': nurse_data['doctor_id']
            }
        }), 200

    def _handle_patient_login(self, email, password):
        """Handle patient login logic"""
        try:
            # Check if patient exists and verify password
            patient = self.patient_model.get_patient_by_email(email)
            if not patient:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Verify password
            if not self.patient_model.verify_password(patient['_id'], password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Generate JWT token
            token_data = {
                'user_id': str(patient['_id']),
                'email': patient['email'],
                'username': patient['username'],
                'role': 'patient'
            }
            token = self.jwt_service.generate_token(token_data)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': str(patient['_id']),
                    'email': patient['email'],
                    'username': patient['username'],
                    'role': 'patient'
                }
            }), 200
        except Exception as e:
            print(f"Patient login error: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def doctor_reset_password(self, request) -> tuple:
        """Reset doctor password"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            new_password = data.get('new_password', '').strip()
            otp = data.get('otp', '').strip()
            
            jwt_token = data.get('jwt_token', '').strip()
            
            if not all([email, new_password, otp, jwt_token]):
                return jsonify({'error': 'Email, new password, OTP, and JWT token are required'}), 400
            
            # Verify JWT OTP first
            verification_result = self.jwt_service.verify_otp_jwt(jwt_token, email, otp)
            if not verification_result['success']:
                return jsonify({'error': verification_result['error']}), 400
            
            # Reset password
            result = self.doctor_model.reset_password(email, new_password)
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Password reset successfully'
                }), 200
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def doctor_forgot_password(self, request) -> tuple:
        """Forgot doctor password - send reset OTP"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            
            # Check if doctor exists
            doctor = self.doctor_model.get_doctor_by_email(email)
            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404
            
            # Generate JWT-based OTP for password reset
            try:
                otp, jwt_token = self.jwt_service.generate_otp_jwt(email, 'doctor_password_reset', {'email': email})
                print(f"🔐 Generated JWT OTP for password reset: {otp} for email: {email}")
            except Exception as e:
                return jsonify({
                    'error': f'Failed to generate OTP: {str(e)}'
                }), 500
            
            # Send OTP email
            email_result = self.email_service.send_otp_email(email, otp)
            
            if email_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'OTP sent to your email for password reset',
                    'email': email,
                    'jwt_token': jwt_token,
                    'otp': otp
                }), 200
            else:
                return jsonify({'error': 'Failed to send OTP email'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500