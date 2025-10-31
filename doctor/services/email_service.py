"""
Email Service - Handles all email operations
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
from typing import Dict, Any, Optional

class EmailService:
    """Email service for sending emails"""
    
    def __init__(self):
        self.sender_email = os.environ.get('SENDER_EMAIL', 'ramya.sureshkumar.lm@gmail.com')
        self.sender_password = os.environ.get('SENDER_PASSWORD', 'djqs dktf gqor gnqg')
        # Try multiple SMTP configurations
        self.smtp_configs = [
            {'server': 'smtp.gmail.com', 'port': 587},
            {'server': 'smtp.gmail.com', 'port': 465},
            {'server': 'smtp-mail.outlook.com', 'port': 587},
            {'server': 'smtp-mail.outlook.com', 'port': 465}
        ]
        self.current_config = 0
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> Dict[str, Any]:
        """Send email"""
        try:
            # Check if email configuration is available
            if not self.sender_email or not self.sender_password:
                print("❌ Email configuration not found")
                return {
                    'success': False,
                    'error': 'Email configuration not found'
                }
            
            # Create message
            msg = MIMEMultipart('mixed')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Reply-To'] = self.sender_email
            msg['X-Mailer'] = 'Patient Alert System'
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                # Send plain text without base64 encoding
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Connect to server and send email
            print(f"📧 Attempting to send email to: {to_email}")
            print(f"📧 EMAIL DEBUG INFO:")
            print(f"   To: {to_email}")
            print(f"   From: {self.sender_email}")
            print(f"   Subject: {subject}")
            print(f"   Body length: {len(body)} characters")
            
            # Try multiple SMTP configurations
            last_error = None
            for i, config in enumerate(self.smtp_configs):
                try:
                    print(f"📧 Trying SMTP config {i+1}/{len(self.smtp_configs)}: {config['server']}:{config['port']}")
                    
                    if config['port'] == 465:
                        # Use SSL for port 465
                        with smtplib.SMTP_SSL(config['server'], config['port']) as server:
                            print("📧 Connected via SSL...")
                            server.login(self.sender_email, self.sender_password)
                            print("📧 Logged in successfully...")
                            server.send_message(msg)
                            print("✅ Email sent successfully via SSL")
                            return {
                                'success': True,
                                'message': f'Email sent successfully via {config["server"]}:{config["port"]}'
                            }
                    else:
                        # Use STARTTLS for port 587
                        with smtplib.SMTP(config['server'], config['port']) as server:
                            print("📧 Connected to SMTP...")
                            server.starttls()
                            print("📧 Started TLS...")
                            server.login(self.sender_email, self.sender_password)
                            print("📧 Logged in successfully...")
                            server.send_message(msg)
                            print("✅ Email sent successfully via STARTTLS")
                            return {
                                'success': True,
                                'message': f'Email sent successfully via {config["server"]}:{config["port"]}'
                            }
                            
                except Exception as e:
                    print(f"❌ Failed with config {i+1}: {e}")
                    last_error = e
                    continue
            
            # If all configurations failed
            print(f"❌ All SMTP configurations failed. Last error: {last_error}")
            return {
                'success': False,
                'error': f'All SMTP configurations failed. Last error: {str(last_error)}'
            }
                
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Error: {e}")
            return {
                'success': False,
                'error': 'SMTP authentication failed. Please check email credentials.'
            }
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ SMTP Recipients Refused: {e}")
            return {
                'success': False,
                'error': 'Recipient email address is invalid or refused.'
            }
        except smtplib.SMTPServerDisconnected as e:
            print(f"❌ SMTP Server Disconnected: {e}")
            return {
                'success': False,
                'error': 'SMTP server disconnected unexpectedly.'
            }
        except Exception as e:
            print(f"❌ Email sending error: {e}")
            return {
                'success': False,
                'error': f'Failed to send email: {str(e)}'
            }
    
    def send_otp_email(self, email: str, otp: str) -> Dict[str, Any]:
        """Send OTP email"""
        try:
            subject = "Patient Alert System - OTP Verification"
            body = f"""    Hello!
    
    Your OTP for Patient Alert System is: {otp}
    
    This OTP is valid for 10 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Patient Alert System Team
    
    """
            
            result = self.send_email(email, subject, body)
            
            if result['success']:
                print(f"✅ OTP email sent to: {email}")
                print(f"📧 Check your email in 1-2 minutes")
                print("✅ Primary email method successful")
            else:
                print(f"❌ Failed to send OTP email: {result['error']}")
                print(f"🔐 OTP for manual verification: {otp}")
                print("📧 Alternative: Check your email manually")
                print("=" * 50)
                print("📧 EMAIL CONTENT (for manual verification):")
                print(f"To: {email}")
                print(f"Subject: {subject}")
                print(f"Body: {body}")
                print("=" * 50)
            
            return result
            
        except Exception as e:
            print(f"❌ OTP email error: {e}")
            print(f"🔐 OTP for manual verification: {otp}")
            print("=" * 50)
            print("📧 EMAIL CONTENT (for manual verification):")
            print(f"To: {email}")
            print(f"Subject: Patient Alert System - OTP Verification")
            print(f"Body: Your OTP is: {otp}")
            print("=" * 50)
            return {
                'success': False,
                'error': f'Failed to send OTP email: {str(e)}'
            }
    
    def send_welcome_email(self, email: str, name: str, user_type: str) -> Dict[str, Any]:
        """Send welcome email"""
        try:
            subject = f"Welcome to Patient Alert System - {user_type.title()}"
            body = f"""    Hello {name}!
    
    Welcome to Patient Alert System!
    
    Your {user_type} account has been created successfully.
    
    You can now access all the features of our platform.
    
    Best regards,
    Patient Alert System Team
    
    """
            
            return self.send_email(email, subject, body)
            
        except Exception as e:
            print(f"❌ Welcome email error: {e}")
            return {
                'success': False,
                'error': f'Failed to send welcome email: {str(e)}'
            }
    
    def send_invite_email(self, patient_email: str, invite_code: str, doctor_info: dict, custom_message: str = '') -> Dict[str, Any]:
        """Send invite email to patient"""
        try:
            doctor_name = doctor_info.get('name', 'Doctor')
            doctor_specialty = doctor_info.get('specialty', 'General Practice')
            doctor_hospital = doctor_info.get('hospital', '')
            
            subject = f"Doctor Invitation - {doctor_name} wants to connect with you"
            
            body = f"""Dear Patient,

You have received a doctor invitation from Patient Alert System.

Doctor Details:
- Name: Dr. {doctor_name}
- Specialty: {doctor_specialty}
- Hospital: {doctor_hospital}

Invitation Details:
- Invite Code: {invite_code}
- This code expires in 7 days
- You can use this code to connect with the doctor

"""
            
            if custom_message:
                body += f"Personal Message from Dr. {doctor_name}:\n"
                body += f'"{custom_message}"\n\n'
            
            body += """How to Accept:
1. Open the Patient Alert System app
2. Go to "Connect with Doctor"
3. Enter the invite code: """ + invite_code + """
4. Follow the prompts to complete the connection

If you don't have the app, you can download it from your app store.

Best regards,
Patient Alert System Team

---
This is an automated message. Please do not reply to this email.
"""
            
            result = self.send_email(patient_email, subject, body)
            
            if result['success']:
                print(f"✅ Invite email sent to patient: {patient_email}")
                print(f"📧 Invite code: {invite_code}")
            else:
                print(f"❌ Failed to send invite email: {result['error']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Invite email error: {e}")
            return {
                'success': False,
                'error': f'Failed to send invite email: {str(e)}'
            }
    
    def is_configured(self) -> bool:
        """Check if email service is configured"""
        return bool(self.sender_email and self.sender_password)
    
    def test_network_connectivity(self) -> Dict[str, Any]:
        """Test network connectivity to SMTP servers"""
        import socket
        
        results = {}
        for config in self.smtp_configs:
            try:
                print(f"🔍 Testing connectivity to {config['server']}:{config['port']}")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)  # 10 second timeout
                result = sock.connect_ex((config['server'], config['port']))
                sock.close()
                
                if result == 0:
                    print(f"✅ {config['server']}:{config['port']} - Connected")
                    results[f"{config['server']}:{config['port']}"] = "Connected"
                else:
                    print(f"❌ {config['server']}:{config['port']} - Failed (Error: {result})")
                    results[f"{config['server']}:{config['port']}"] = f"Failed (Error: {result})"
                    
            except Exception as e:
                print(f"❌ {config['server']}:{config['port']} - Exception: {e}")
                results[f"{config['server']}:{config['port']}"] = f"Exception: {e}"
        
        return results
