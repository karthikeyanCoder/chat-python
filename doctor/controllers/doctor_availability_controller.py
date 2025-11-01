"""
Doctor Availability Controller - Complete Implementation
"""

from flask import request, jsonify
from datetime import datetime
import re

class DoctorAvailabilityController:
    """Controller for doctor availability management"""
    
    def __init__(self, availability_model, jwt_service, validators):
        self.availability_model = availability_model
        self.jwt_service = jwt_service
        self.validators = validators
    
    def create_availability(self, request, doctor_id: str):
        """Create availability slots for doctor"""
        try:
            data = request.get_json()

            # Adapter A: If neither 'types' nor 'slots' provided, auto-generate 30-min slots from work_hours and breaks
            def _generate_slots_30m(work_hours: dict, breaks: list):
                import datetime as dt
                def to_time(s):
                    return dt.datetime.strptime(s, "%H:%M").time()
                def minutes(t):
                    return t.hour * 60 + t.minute
                def overlap(a_start, a_end, b_start, b_end):
                    return not (a_end <= b_start or a_start >= b_end)

                if not isinstance(work_hours, dict) or 'start_time' not in work_hours or 'end_time' not in work_hours:
                    return []
                start = to_time(work_hours['start_time'])
                end = to_time(work_hours['end_time'])
                work_start, work_end = minutes(start), minutes(end)
                blocked = []
                for br in (breaks or []):
                    try:
                        bs, be = minutes(to_time(br['start_time'])), minutes(to_time(br['end_time']))
                        blocked.append((bs, be))
                    except Exception:
                        continue

                slots = []
                cur = work_start
                slot_index = 1
                while cur + 30 <= work_end:
                    ns = cur
                    ne = cur + 30
                    if not any(overlap(ns, ne, b[0], b[1]) for b in blocked):
                        s_h, s_m = divmod(ns, 60)
                        e_h, e_m = divmod(ne, 60)
                        slots.append({
                            'slot_id': f"slot_{slot_index:03d}",
                            'start_time': f"{s_h:02d}:{s_m:02d}",
                            'end_time': f"{e_h:02d}:{e_m:02d}",
                            'is_booked': False
                        })
                        slot_index += 1
                    cur += 30
                return slots

            if 'types' not in data and 'slots' not in data:
                auto_slots = _generate_slots_30m(data.get('work_hours') or {}, data.get('breaks', []))
                if auto_slots:
                    data['slots'] = auto_slots

            # Adapter B: Accept top-level slots and wrap into a default appointment type
            if 'types' not in data and isinstance(data.get('slots'), list):
                wrapped_slots = []
                slot_counter = 1
                for s in data['slots']:
                    slot = dict(s)
                    if 'slot_id' not in slot or not slot.get('slot_id'):
                        slot['slot_id'] = f"slot_{slot_counter:03d}"
                    wrapped_slots.append(slot)
                    slot_counter += 1
                
                data['types'] = [{
                    'type': data.get('appointment_type', 'General Consultation'),
                    'duration_mins': data.get('duration_mins', 30),
                    'price': data.get('price', 0.0),
                    'currency': data.get('currency', 'USD'),
                    'slots': wrapped_slots
                }]
                data.pop('slots', None)
            
            # Validate required fields
            required_fields = ['date', 'work_hours', 'types', 'consultation_type']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'{field} is required'
                    }), 400
            
            # Validate date format
            if not self._validate_date_format(data['date']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Validate work hours
            if not self._validate_work_hours(data['work_hours']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid work hours format'
                }), 400
            
            # Validate consultation type
            if data['consultation_type'] not in ['Online', 'In-Person']:
                return jsonify({
                    'success': False,
                    'error': 'Consultation type must be "Online" or "In-Person"'
                }), 400
            
            # Validate appointment types
            if not self._validate_appointment_types(data['types']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid appointment types structure'
                }), 400
            
            # Create availability
            result = self.availability_model.create_daily_availability(doctor_id, data['date'], data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Availability created successfully',
                    'availability_id': result['availability_id']
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to create availability: {str(e)}'
            }), 500
    
    def get_availability(self, request, doctor_id: str):
        """Get doctor's availability"""
        try:
            # Get query parameters
            date = request.args.get('date')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            consultation_type = request.args.get('consultation_type')
            appointment_type = request.args.get('appointment_type')  # optional filter for types.type
            
            # Validate date parameters
            if date and not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            if start_date and end_date:
                if not self._validate_date_format(start_date) or not self._validate_date_format(end_date):
                    return jsonify({
                        'success': False,
                        'error': 'Invalid date range format. Use YYYY-MM-DD'
                    }), 400
                
                date_range = {'start_date': start_date, 'end_date': end_date}
            else:
                date_range = None
            
            # Get availability (optionally filter by consultation type)
            result = self.availability_model.get_doctor_availability(doctor_id, date, date_range, consultation_type)

            # If appointment_type provided, filter types within each availability doc
            if result.get('success') and appointment_type:
                filtered = []
                for avail in result.get('availability', []):
                    types_arr = avail.get('types', [])
                    kept_types = [t for t in types_arr if str(t.get('type', '')).strip() == appointment_type]
                    if kept_types:
                        # Make a shallow copy to avoid mutating original
                        new_avail = dict(avail)
                        new_avail['types'] = kept_types
                        filtered.append(new_avail)
                result['availability'] = filtered
                result['total_count'] = len(filtered)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'availability': result['availability'],
                    'total_count': result['total_count']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get availability: {str(e)}'
            }), 500
    
    def get_availability_by_date(self, request, doctor_id: str, date: str):
        """Get doctor's availability for specific date"""
        try:
            consultation_type = request.args.get('consultation_type')
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Get availability for specific date (optionally filter by consultation type)
            result = self.availability_model.get_doctor_availability(doctor_id, date, None, consultation_type)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'availability': result['availability'],
                    'total_count': result['total_count']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get availability by date: {str(e)}'
            }), 500
    
    def get_available_slots_by_type(self, request, doctor_id: str, date: str, appointment_type: str):
        """Get available slots for specific appointment type"""
        try:
            consultation_type = request.args.get('consultation_type')
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Get available slots (optionally filter by consultation type)
            result = self.availability_model.get_available_slots_by_type(doctor_id, date, appointment_type, consultation_type)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'slots': result['slots'],
                    'total_available': result['total_available'],
                    'doctor_id': doctor_id,
                    'date': date,
                    'appointment_type': appointment_type
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get available slots: {str(e)}'
            }), 500
    
    def update_availability(self, request, availability_id: str):
        """Update availability document"""
        try:
            data = request.get_json()
            
            # Validate date if provided
            if 'date' in data and not self._validate_date_format(data['date']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Validate work hours if provided
            if 'work_hours' in data and not self._validate_work_hours(data['work_hours']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid work hours format'
                }), 400
            
            # Update availability
            result = self.availability_model.update_availability(availability_id, data)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Availability updated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to update availability: {str(e)}'
            }), 500
    
    def delete_availability(self, request, availability_id: str):
        """Delete availability document"""
        try:
            # Delete availability
            result = self.availability_model.delete_availability(availability_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Availability deleted successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to delete availability: {str(e)}'
            }), 500
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _validate_work_hours(self, work_hours: dict) -> bool:
        """Validate work hours format"""
        try:
            required_fields = ['start_time', 'end_time']
            for field in required_fields:
                if field not in work_hours:
                    return False
            
            # Validate time format HH:MM
            time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
            if not re.match(time_pattern, work_hours['start_time']) or not re.match(time_pattern, work_hours['end_time']):
                return False
            
            return True
        except:
            return False
    
    def _validate_appointment_types(self, types: list) -> bool:
        """Validate appointment types structure"""
        try:
            if not isinstance(types, list) or len(types) == 0:
                return False
            
            for appointment_type in types:
                required_fields = ['type', 'duration_mins', 'slots']
                for field in required_fields:
                    if field not in appointment_type:
                        return False
                
                # Validate slots structure
                if not isinstance(appointment_type['slots'], list):
                    return False
                
                for slot in appointment_type['slots']:
                    slot_required_fields = ['start_time', 'end_time', 'is_booked']
                    for field in slot_required_fields:
                        if field not in slot:
                            return False
            
            return True
        except:
            return False
    
    def cancel_appointment_slot(self, request, doctor_id: str, date: str, slot_id: str):
        """Cancel a specific appointment slot"""
        try:
            data = request.get_json()
            appointment_id = data.get('appointment_id')
            cancellation_reason = data.get('cancellation_reason', 'Cancelled by doctor')
            consultation_type = request.args.get('consultation_type')
            
            if not appointment_id:
                return jsonify({
                    'success': False,
                    'error': 'appointment_id is required'
                }), 400
            
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Cancel the slot (optionally filter by consultation type)
            result = self.availability_model.cancel_appointment_slot(
                doctor_id, date, slot_id, appointment_id, cancellation_reason, consultation_type
            )
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Appointment slot cancelled successfully',
                    'slot_id': slot_id,
                    'appointment_id': appointment_id
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to cancel appointment slot: {str(e)}'
            }), 500
    
    def book_slot(self, request, doctor_id: str, date: str):
        """Book a specific availability slot"""
        try:
            data = request.get_json()
            consultation_type = request.args.get('consultation_type')
            
            # Validate required fields
            required_fields = ['slot_id', 'patient_id', 'appointment_id']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'{field} is required'
                    }), 400
            
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            slot_id = data['slot_id']
            patient_id = data['patient_id']
            appointment_id = data['appointment_id']
            
            # Call model to book the slot
            result = self.availability_model.book_slot(
                doctor_id=doctor_id,
                date=date,
                slot_id=slot_id,
                patient_id=patient_id,
                appointment_id=appointment_id,
                consultation_type=consultation_type
            )
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'doctor_id': doctor_id,
                    'date': date,
                    'slot_id': slot_id,
                    'patient_id': patient_id,
                    'appointment_id': appointment_id
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to book slot: {str(e)}'
            }), 500
    
    def get_booked_slots(self, request, doctor_id: str, date: str):
        """Get all booked slots for a specific date"""
        try:
            consultation_type = request.args.get('consultation_type')
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Get booked slots (optionally filter by consultation type)
            result = self.availability_model.get_booked_slots_by_date(doctor_id, date, consultation_type)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'booked_slots': result['booked_slots'],
                    'total_booked': result['total_booked'],
                    'doctor_id': doctor_id,
                    'date': date
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get booked slots: {str(e)}'
            }), 500
    
    def get_available_slots_only(self, request, doctor_id: str, date: str):
        """Get only unbooked slots for a date in simple format"""
        try:
            consultation_type = request.args.get('consultation_type')
            
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Get availability for the date
            result = self.availability_model.get_doctor_availability(
                doctor_id, date, None, consultation_type
            )
            
            if not result.get('success'):
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to get availability')
                }), 500
            
            # Collect all unbooked slots
            all_slots = []
            for avail in result.get('availability', []):
                for t in avail.get('types', []):
                    for slot in t.get('slots', []):
                        if not slot.get('is_booked'):
                            all_slots.append({
                                'start_time': slot.get('start_time'),
                                'end_time': slot.get('end_time'),
                                'is_booked': False
                            })
            
            return jsonify({
                'success': True,
                'slots': all_slots
            }), 200
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get available slots: {str(e)}'
            }), 500
    
    def cancel_all_appointments_for_date(self, request, doctor_id: str, date: str):
        """Cancel all appointments for a specific date"""
        try:
            data = request.get_json() or {}
            cancellation_reason = data.get('cancellation_reason', 'Full day cancelled by doctor')
            consultation_type = request.args.get('consultation_type')
            
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Get appointment summary first
            summary_result = self.availability_model.get_date_appointment_summary(doctor_id, date)
            if not summary_result['success']:
                return jsonify({
                    'success': False,
                    'error': summary_result['error']
                }), 400
            
            # Cancel all appointments
            result = self.availability_model.cancel_all_appointments_for_date(
                doctor_id, date, cancellation_reason, consultation_type
            )
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result.get('message', 'All appointments cancelled'),
                    'cancelled_count': result.get('cancelled_count', 0),
                    'cancelled_appointments': result.get('cancelled_appointments', []),
                    'date': date,
                    'doctor_id': doctor_id,
                    'cancellation_reason': cancellation_reason
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to cancel appointments: {str(e)}'
            }), 500
    
    def get_date_appointment_summary(self, request, doctor_id: str, date: str):
        """Get summary of all appointments for a specific date"""
        try:
            consultation_type = request.args.get('consultation_type')
            # Validate date format
            if not self._validate_date_format(date):
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
            
            # Get appointment summary
            result = self.availability_model.get_date_appointment_summary(doctor_id, date, consultation_type)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'summary': result
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get appointment summary: {str(e)}'
            }), 500
