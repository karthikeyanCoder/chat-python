"""
OTP Controller - Handles OTP operations
"""

from flask import request, jsonify
from typing import Dict, Any

class OTPController:
    """OTP controller"""
    
    def __init__(self, otp_model, jwt_service, email_service, validators):
        self.otp_model = otp_model
        self.jwt_service = jwt_service
        self.email_service = email_service
        self.validators = validators
    
    def doctor_send_otp(self, request) -> tuple:
        """Send OTP to doctor email"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            purpose = data.get('purpose', 'signup')
            
            if not email:
                return jsonify({"error": "Email is required"}), 400
            
            if purpose == 'signup':
                # Check if there's a pending signup for this email
                pending_signup = self.otp_model.get_temp_signup_data(email)
                if not pending_signup:
                    return jsonify({
                        "error": "No pending signup found for this email. Please sign up first."
                    }), 400
                
                # Get the original signup data
                signup_data = pending_signup.get('signup_data', {})
                if not signup_data:
                    return jsonify({
                        "error": "Signup data not found. Please sign up again."
                    }), 400
                
                # Generate JWT-based OTP with original signup data
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
                
                if email_result['success']:
                    return jsonify({
                        'success': True,
                        'message': 'OTP sent successfully for signup verification',
                        'email': email,
                        'jwt_token': jwt_token,
                        'otp': otp,
                        'token_info': {
                            'token_length': len(jwt_token),
                            'token_preview': jwt_token[:50] + '...',
                            'expires_in': '10 minutes',
                            'purpose': 'doctor_signup_verification'
                        }
                    }), 200
                else:
                    return jsonify({
                        'error': 'Failed to send OTP email. Please check your email configuration.',
                        'jwt_token': jwt_token,
                        'otp': otp,
                        'token_info': {
                            'token_length': len(jwt_token),
                            'token_preview': jwt_token[:50] + '...',
                            'expires_in': '10 minutes',
                            'purpose': 'doctor_signup_verification'
                        }
                    }), 500
                    
            elif purpose == 'password_reset':
                # Handle password reset OTP
                return jsonify({
                    'error': 'Password reset OTP not implemented yet'
                }), 501
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def doctor_verify_otp(self, request) -> tuple:
        """Verify doctor OTP"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            otp = data.get('otp', '').strip()
            jwt_token = data.get('jwt_token', '').strip()
            
            if not all([email, otp, jwt_token]):
                return jsonify({'error': 'Email, OTP, and JWT token are required'}), 400
            
            # Verify JWT OTP
            verification_result = self.jwt_service.verify_otp_jwt(jwt_token, email, otp)
            
            if not verification_result['success']:
                return jsonify({'error': verification_result['error']}), 400
            
            # Get signup data from JWT
            signup_data = verification_result['data'].get('signup_data', {})
            if not signup_data:
                return jsonify({'error': 'Signup data not found in token'}), 400
            
            # Create doctor account
            from models.doctor_model import DoctorModel
            doctor_model = DoctorModel(self.otp_model.db)
            
            # Update collection reference
            doctor_model._update_collection()
            
            create_result = doctor_model.create_doctor(signup_data)
            if not create_result['success']:
                return jsonify({'error': create_result['error']}), 500
            
            doctor_id = create_result['doctor_id']
            
            # Verify email
            verify_result = doctor_model.verify_doctor_email(doctor_id)
            if not verify_result['success']:
                print(f"⚠️ Email verification failed: {verify_result['error']}")
            
            # Generate access and refresh tokens
            try:
                access_token = self.jwt_service.create_access_token(
                    doctor_id, email, signup_data['username'], 'doctor', 'doctor', 'pending_profile'
                )
                refresh_token = self.jwt_service.create_refresh_token(doctor_id, 'doctor')
                
                print(f"🔑 Access token created for {email}")
                print(f"🔄 Refresh token created for {doctor_id}")
                print(f"✅ Doctor account created successfully: {doctor_id}")
                
                # Clean up temporary data
                cleanup_result = self.otp_model.cleanup_temp_data(email)
                if cleanup_result['success']:
                    print(f"🗑️ Cleaned up temporary signup data for email: {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'Doctor account created successfully! Please complete your profile.',
                    'doctor_id': doctor_id,
                    'email': email,
                    'username': signup_data['username'],
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'status': 'pending_profile'
                }), 200
                
            except Exception as e:
                print(f"❌ Token generation error: {e}")
                return jsonify({'error': f'Token generation failed: {str(e)}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def resend_otp(self, request) -> tuple:
        """Resend OTP"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            role = data.get('role', 'doctor')
            
            if not email:
                return jsonify({"error": "Email is required"}), 400
            
            if role == 'doctor':
                # Check if there's a pending signup for this email
                pending_signup = self.otp_model.get_temp_signup_data(email)
                if not pending_signup:
                    return jsonify({
                        "error": "No pending signup found for this email. Please sign up first."
                    }), 400
                
                # Get the original signup data
                signup_data = pending_signup.get('signup_data', {})
                if not signup_data:
                    return jsonify({
                        "error": "Signup data not found. Please sign up again."
                    }), 400
                
                # Generate new JWT-based OTP
                try:
                    otp, jwt_token = self.jwt_service.generate_otp_jwt(email, 'doctor_signup', signup_data)
                    print(f"🔐 Generated new OTP: {otp} for email: {email}")
                except Exception as e:
                    return jsonify({
                        "error": f"Failed to generate OTP: {str(e)}"
                    }), 500
                
                # Send OTP email
                email_result = self.email_service.send_otp_email(email, otp)
                
                if email_result['success']:
                    return jsonify({
                        'success': True,
                        'message': 'OTP resent successfully',
                        'email': email,
                        'jwt_token': jwt_token,
                        'otp': otp
                    }), 200
                else:
                    return jsonify({
                        'error': 'Failed to send OTP email. Please check your email configuration.',
                        'jwt_token': jwt_token,
                        'otp': otp
                    }), 500
            else:
                return jsonify({
                    'error': 'Resend OTP not supported for this role'
                }), 400
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    def patient_verify_otp(self, request) -> tuple:
        """Verify patient OTP"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            otp = data.get('otp', '').strip()
            
            if not all([email, otp]):
                return jsonify({'error': 'Email and OTP are required'}), 400
            
            # For now, just return success (implement patient OTP verification later)
            return jsonify({
                'success': True,
                'message': 'Patient OTP verification not implemented yet'
            }), 200
                
        except Exception as e:
            return jsonify({'error': f'Server error: {str(e)}'}), 500
