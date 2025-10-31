"""
Scheduler Service - Background task scheduler for appointment reminders
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduling background tasks"""
    
    def __init__(self, db, email_service, reminder_service):
        """
        Initialize scheduler service
        
        Args:
            db: Database instance
            email_service: EmailService instance
            reminder_service: AppointmentReminderService instance
        """
        self.db = db
        self.email_service = email_service
        self.reminder_service = reminder_service
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        try:
            if self.is_running:
                logger.warning("Scheduler is already running")
                return
            
            # Add job to check for upcoming appointments
            check_interval = int(os.environ.get('SCHEDULER_CHECK_INTERVAL', 60))
            
            self.scheduler.add_job(
                self.check_upcoming_appointments,
                trigger=IntervalTrigger(minutes=check_interval),
                id='check_appointments',
                name='Check for upcoming appointments',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Scheduler started with {check_interval} minute interval")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    def check_upcoming_appointments(self):
        """
        Check for upcoming appointments and send reminders
        
        This method runs periodically based on SCHEDULER_CHECK_INTERVAL
        """
        try:
            logger.info("Checking for upcoming appointments...")
            
            # Get appointments from database
            appointments = self.db.get_upcoming_appointments(hours_ahead=24)
            
            if not appointments:
                logger.info("No upcoming appointments found")
                return
            
            logger.info(f"Found {len(appointments)} upcoming appointments")
            
            # Send reminders for each appointment
            for appointment in appointments:
                try:
                    result = self.send_reminders_for_appointment(appointment)
                    if result.get('success'):
                        logger.info(f"Reminder sent for appointment {appointment.get('appointment_id')}")
                    else:
                        logger.error(f"Failed to send reminder: {result.get('error')}")
                except Exception as e:
                    logger.error(f"Error processing appointment: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error checking upcoming appointments: {str(e)}")
    
    def send_reminders_for_appointment(self, appointment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send reminder email for a specific appointment
        
        Args:
            appointment: Appointment dictionary with patient info
        
        Returns:
            dict: Result of reminder sending
        """
        try:
            # Extract appointment details
            patient_email = appointment.get('patient_email')
            patient_name = appointment.get('patient_name')
            doctor_name = appointment.get('doctor_name', 'Your Doctor')
            appointment_date = appointment.get('appointment_date')
            appointment_time = appointment.get('appointment_time')
            appointment_type = appointment.get('appointment_type', 'Consultation')
            patient_id = appointment.get('patient_id')
            appointment_id = appointment.get('appointment_id')
            
            # Validate required fields
            if not all([patient_email, patient_name, appointment_date, appointment_time]):
                return {
                    'success': False,
                    'error': 'Missing required appointment details'
                }
            
            # Check if reminder already sent
            if appointment.get('reminder_sent'):
                logger.info(f"Reminder already sent for appointment {appointment_id}")
                return {
                    'success': True,
                    'message': 'Reminder already sent'
                }
            
            # Send reminder email
            result = self.reminder_service.send_appointment_reminder_email(
                patient_email=patient_email,
                patient_name=patient_name,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_type=appointment_type
            )
            
            # Update appointment to mark reminder as sent
            if result.get('success'):
                self._mark_reminder_sent(patient_id, appointment_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending reminder for appointment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _mark_reminder_sent(self, patient_id: str, appointment_id: str):
        """
        Mark appointment reminder as sent in database
        
        Args:
            patient_id: Patient ID
            appointment_id: Appointment ID
        """
        try:
            # Update the appointment in the patient's appointments array
            result = self.db.db['Patient_test'].update_one(
                {
                    'patient_id': patient_id,
                    'appointments.appointment_id': appointment_id
                },
                {
                    '$set': {
                        'appointments.$.reminder_sent': True,
                        'appointments.$.reminder_sent_at': datetime.utcnow().isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Marked reminder as sent for appointment {appointment_id}")
            else:
                logger.warning(f"Could not update reminder status for appointment {appointment_id}")
                
        except Exception as e:
            logger.error(f"Error marking reminder as sent: {str(e)}")

