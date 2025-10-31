"""
Email utilities for sending OTP, notifications, and reminders
"""
import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration now uses direct environment variables
# from .config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM  # Not used


def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using Gmail SMTP"""
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        print(f"[*] Email config check - SENDER_EMAIL: {'[OK] Set' if sender_email else '[ERROR] Missing'}")
        print(f"[*] Email config check - SENDER_PASSWORD: {'[OK] Set' if sender_password else '[ERROR] Missing'}")
        
        if not sender_email or not sender_password:
            print("[ERROR] Email configuration missing - SENDER_EMAIL or SENDER_PASSWORD not set")
            print("[INFO] Please check your .env file contains:")
            print("   SENDER_EMAIL=your_email@gmail.com")
            print("   SENDER_PASSWORD=your_app_password")
            return False  # Return False instead of True for missing config
        
        print(f"[*] Attempting to send email to: {to_email}")
        print(f"[*] From: {sender_email}")
        print(f"[*] Subject: {subject}")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        print("[*] Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("[*] Logging in to Gmail...")
        server.login(sender_email, sender_password)
        
        print("[*] Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print("[OK] Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] SMTP Authentication failed: {e}")
        print("[INFO] Check your Gmail App Password - make sure 2FA is enabled")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[ERROR] Recipient email refused: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"[ERROR] SMTP Server disconnected: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Email sending failed: {e}")
        print(f"[INFO] Error type: {type(e).__name__}")
        return False


def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP email"""
    subject = "Patient Alert System - OTP Verification"
    body = f"""
    Hello!
    
    Your OTP for Patient Alert System is: {otp}
    
    This OTP is valid for 10 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Patient Alert System Team
    """
    print(f"[*] Sending OTP email to: {email}")
    print(f"[*] OTP: {otp}")
    result = send_email(email, subject, body)
    if result:
        print("[OK] OTP email sent successfully!")
    else:
        print("[ERROR] Failed to send OTP email!")
    return result


def send_patient_id_email(email: str, patient_id: str, username: str) -> bool:
    """Send Patient ID to user's email"""
    try:
        subject = "Your Patient ID - Patient Alert System"
        body = f"""
Hello {username},

Your Patient ID has been generated successfully.

Patient ID: {patient_id}

Please keep this ID safe and use it to log in to your account.

Best regards,
Patient Alert System Team
        """
        
        return send_email(email, subject, body)
    except Exception as e:
        print(f"Error sending Patient ID email: {e}")
        return False


def send_medication_reminder_email(email: str, username: str, medication_name: str, dosage: str, time: str, frequency: str, special_instructions: str = "") -> bool:
    """Send medication reminder email to user"""
    try:
        subject = f"Medication Reminder: {medication_name}"
        body = f"""
Hello {username},

It's time to take your medication!

Medication: {medication_name}
Dosage: {dosage}
Time: {time}
Frequency: {frequency}
{f"Special Instructions: {special_instructions}" if special_instructions else ""}

Please take your medication as prescribed by your doctor.
    
    Best regards,
    Patient Alert System Team
    """
        
        return send_email(email, subject, body)
    except Exception as e:
        print(f"Error sending medication reminder email: {e}")
        return False


def check_and_send_medication_reminders(db):
    """Check all patients for upcoming medication dosages and send email reminders"""
    try:
        print("[*] Checking for medication reminders...")
        
        # Get all patients
        patients = db.patients_collection.find({})
        current_time = datetime.now()
        
        reminders_sent = 0
        
        for patient in patients:
            try:
                patient_id = patient.get('patient_id')
                email = patient.get('email')
                username = patient.get('username')
                
                if not all([patient_id, email, username]):
                    continue
                
                # Get medication logs for this patient
                medication_logs = patient.get('medication_logs', [])
                
                for log in medication_logs:
                    if not log.get('is_prescription_mode', False):
                        # Handle multiple dosages
                        dosages = log.get('dosages', [])
                        for dosage in dosages:
                            if dosage.get('reminder_enabled', False):
                                try:
                                    time_str = dosage.get('time', '')
                                    if time_str:
                                        hour, minute = map(int, time_str.split(':'))
                                        dose_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                                        
                                        # Check if it's time to send reminder (within 15 minutes of dose time)
                                        time_diff = abs((current_time - dose_time).total_seconds() / 60)
                                        
                                        if time_diff <= 15:  # Within 15 minutes
                                            if send_medication_reminder_email(
                                                email=email,
                                                username=username,
                                                medication_name=log.get('medication_name', 'Unknown'),
                                                dosage=dosage.get('dosage', ''),
                                                time=time_str,
                                                frequency=dosage.get('frequency', ''),
                                                special_instructions=dosage.get('special_instructions', '')
                                            ):
                                                reminders_sent += 1
                                                print(f"[OK] Medication reminder sent to {email} for {log.get('medication_name')} at {time_str}")
                                            else:
                                                print(f"[ERROR] Failed to send medication reminder to {email}")
                                                
                                except Exception as e:
                                    print(f"[WARN] Error processing dosage reminder for patient {patient_id}: {e}")
                                    continue
                                    
            except Exception as e:
                print(f"[WARN] Error processing patient {patient.get('patient_id', 'unknown')}: {e}")
                continue
        
        print(f"[OK] Medication reminder check completed. {reminders_sent} reminders sent.")
        return reminders_sent
        
    except Exception as e:
        print(f"[ERROR] Error in medication reminder service: {e}")
        return 0

