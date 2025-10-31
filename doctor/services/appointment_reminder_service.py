"""
Appointment Reminder Service - Sends reminder emails for upcoming appointments
"""

import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AppointmentReminderService:
    """Service for sending appointment reminder emails"""
    
    def __init__(self, email_service, db):
        """
        Initialize appointment reminder service
        
        Args:
            email_service: EmailService instance
            db: Database instance
        """
        self.email_service = email_service
        self.db = db
    
    def send_appointment_reminder_email(self, patient_email: str, patient_name: str, 
                                       doctor_name: str, appointment_date: str, 
                                       appointment_time: str, appointment_type: str) -> Dict[str, Any]:
        """
        Send appointment reminder email to patient
        
        Args:
            patient_email: Patient's email address
            patient_name: Patient's name
            doctor_name: Doctor's name
            appointment_date: Appointment date
            appointment_time: Appointment time
            appointment_type: Type of appointment
        
        Returns:
            dict: Result of email sending
        """
        try:
            # Format date and time
            try:
                date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A, %B %d, %Y")
            except:
                formatted_date = appointment_date
            
            # Create email subject
            subject = f"Appointment Reminder - {formatted_date} at {appointment_time}"
            
            # Create email body
            body = f"""Hello {patient_name},

This is a reminder for your upcoming appointment:

Date: {formatted_date}
Time: {appointment_time}
Type: {appointment_type}
Doctor: {doctor_name}

Please arrive 10 minutes early for check-in.

If you need to reschedule, please contact us.

Best regards,
Patient Alert System Team"""
            
            # Send email
            result = self.email_service.send_email(
                to_email=patient_email,
                subject=subject,
                body=body,
                is_html=False
            )
            
            if result.get('success'):
                logger.info(f"Appointment reminder sent to {patient_email}")
            else:
                logger.error(f"Failed to send appointment reminder to {patient_email}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending appointment reminder: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

