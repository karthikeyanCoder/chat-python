"""
Doctor Availability Model - Complete Implementation
Based on the user's proposed model structure
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId

class DoctorAvailabilityModel:
    """Doctor availability model for database operations"""
    
    def __init__(self, db):
        self.db = db
        self.collection = None
        self._update_collection()
    
    def _update_collection(self):
        """Update collection reference"""
        try:
            if self.db and hasattr(self.db, 'doctor_availability_collection'):
                self.collection = self.db.doctor_availability_collection
                print(f"✅ Doctor availability collection updated")
                # Ensure required indexes exist (idempotent)
                if self.collection is not None:
                    try:
                        self.collection.create_index(
                            [("doctor_id", 1), ("date", 1), ("consultation_type", 1)],
                            unique=True,
                            name="uniq_doctor_date_type"
                        )
                    except Exception as e:
                        error_msg = str(e)
                        # Non-fatal; continue if index already exists or cannot be created now
                        if 'IndexKeySpecsConflict' in error_msg or 'already exists' in error_msg.lower():
                            pass  # Index already exists, that's fine
                        else:
                            print(f"⚠️  Could not ensure unique index uniq_doctor_date_type: {e}")
                else:
                    print(f"⚠️  Doctor availability collection is None, skipping index creation")
            else:
                print(f"❌ Doctor availability collection not available")
                self.collection = None
        except Exception as e:
            print(f"❌ Error updating doctor availability collection: {e}")
            self.collection = None
    
    def create_daily_availability(self, doctor_id: str, date: str, availability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create availability for a specific date using your model structure"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Check if availability already exists for this date and consultation type
            existing = self.collection.find_one({
                'doctor_id': doctor_id,
                'date': date,
                'consultation_type': availability_data['consultation_type']
            })
            
            if existing:
                return {
                    'success': False,
                    'error': 'Availability already exists for this date and consultation type'
                }
            
            # Generate unique availability ID
            availability_id = f"AVAIL_{int(time.time() * 1000)}{uuid.uuid4().hex[:8].upper()}"
            
            # Process and validate appointment types
            processed_types = self._process_appointment_types(availability_data.get('types', []))
            
            # Create availability document using your model structure
            availability_doc = {
                'availability_id': availability_id,
                'doctor_id': doctor_id,
                'date': date,
                'work_hours': availability_data['work_hours'],
                'consultation_type': availability_data['consultation_type'],
                'types': processed_types,
                'breaks': availability_data.get('breaks', []),
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Insert availability
            result = self.collection.insert_one(availability_doc)
            
            if result.inserted_id:
                return {
                    'success': True,
                    'availability_id': availability_id,
                    'message': 'Availability created successfully',
                    'inserted_id': str(result.inserted_id)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create availability'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def _process_appointment_types(self, types: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process appointment types with slot generation"""
        processed_types = []
        
        for appointment_type in types:
            # Generate slots for this appointment type
            slots = self._generate_slots_for_type(appointment_type)
            
            # Calculate slot counts
            available_count = len([s for s in slots if not s.get('is_booked', False)])
            total_count = len(slots)
            
            processed_type = {
                'type': appointment_type['type'],
                'duration_mins': appointment_type['duration_mins'],
                'price': appointment_type.get('price', 0.0),
                'currency': appointment_type.get('currency', 'USD'),
                'available_slots_count': available_count,
                'total_slots_count': total_count,
                'slots': slots
            }
            
            processed_types.append(processed_type)
        
        return processed_types
    
    def _generate_slots_for_type(self, appointment_type: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate slots for appointment type"""
        slots = []
        predefined_slots = appointment_type.get('slots', [])
        
        if predefined_slots:
            # Use predefined slots
            for i, slot in enumerate(predefined_slots):
                slot_id = slot.get('slot_id', f"slot_{i+1:03d}")
                processed_slot = {
                    'slot_id': slot_id,
                    'start_time': slot['start_time'],
                    'end_time': slot['end_time'],
                    'is_booked': slot.get('is_booked', False),
                    'patient_id': slot.get('patient_id'),
                    'appointment_id': slot.get('appointment_id'),
                    'booking_timestamp': slot.get('booking_timestamp'),
                    'cancellation_reason': slot.get('cancellation_reason'),
                    'notes': slot.get('notes', '')
                }
                slots.append(processed_slot)
        else:
            # Auto-generate slots based on work hours and duration
            slots = self._auto_generate_slots(appointment_type)
        
        return slots
    
    def _auto_generate_slots(self, appointment_type: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Auto-generate slots based on duration and work hours"""
        # This would integrate with work_hours to generate slots
        # For now, return empty list - slots should be predefined
        return []
    
    def get_doctor_availability(self, doctor_id: str, date: str = None, date_range: Dict[str, str] = None, consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get doctor's availability"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Build query
            query = {'doctor_id': doctor_id, 'is_active': True}
            
            if date:
                query['date'] = date
            elif date_range:
                query['date'] = {
                    '$gte': date_range['start_date'],
                    '$lte': date_range['end_date']
                }

            if consultation_type:
                query['consultation_type'] = consultation_type
            
            # Get availability
            availability_cursor = self.collection.find(query).sort('date', 1)
            availability_list = list(availability_cursor)
            
            # Convert ObjectIds to strings
            for avail in availability_list:
                if '_id' in avail:
                    avail['_id'] = str(avail['_id'])
            
            return {
                'success': True,
                'availability': availability_list,
                'total_count': len(availability_list)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_available_slots_by_type(self, doctor_id: str, date: str, appointment_type: str, consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get available slots for specific appointment type"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Use aggregation to get available slots
            pipeline = [
                {
                    "$match": {
                        "doctor_id": doctor_id,
                        "date": date,
                        "is_active": True
                    }
                },
            ]

            if consultation_type:
                pipeline[0]["$match"]["consultation_type"] = consultation_type

            pipeline.extend([
                {
                    "$unwind": "$types"
                },
                {
                    "$match": {
                        "types.type": appointment_type
                    }
                },
                {
                    "$unwind": "$types.slots"
                },
                {
                    "$match": {
                        "$or": [
                            {"types.slots.is_booked": False},
                            {"types.slots.is_booked": "false"},
                            {"types.slots.is_booked": {"$ne": True}},
                            {"types.slots.is_booked": {"$ne": "true"}}
                        ]
                    }
                },
                {
                    "$project": {
                        "availability_id": 1,
                        "doctor_id": 1,
                        "date": 1,
                        "consultation_type": 1,
                        "appointment_type": "$types.type",
                        "slot_id": "$types.slots.slot_id",
                        "start_time": "$types.slots.start_time",
                        "end_time": "$types.slots.end_time",
                        "duration_mins": "$types.duration_mins",
                        "price": "$types.price",
                        "currency": "$types.currency",
                        "is_booked": "$types.slots.is_booked",
                        "notes": "$types.slots.notes"
                    }
                }
            ])
            
            available_slots = list(self.collection.aggregate(pipeline))
            
            # Convert ObjectIds to strings
            for slot in available_slots:
                if '_id' in slot:
                    slot['_id'] = str(slot['_id'])
            
            return {
                'success': True,
                'slots': available_slots,
                'total_available': len(available_slots)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def book_slot(self, doctor_id: str, date: str, slot_id: str, patient_id: str, appointment_id: str, consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Book a specific availability slot"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Find and update the specific slot
            match_query = {
                'doctor_id': doctor_id,
                'date': date
            }
            if consultation_type:
                match_query['consultation_type'] = consultation_type

            result = self.collection.update_one(
                match_query,
                {
                    '$set': {
                        'types.$[type].slots.$[slot].is_booked': True,
                        'types.$[type].slots.$[slot].patient_id': patient_id,
                        'types.$[type].slots.$[slot].appointment_id': appointment_id,
                        'types.$[type].slots.$[slot].booking_timestamp': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                },
                array_filters=[
                    {'type.type': {'$exists': True}},
                    {'slot.slot_id': slot_id, 'slot.is_booked': False}
                ]
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Slot booked successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Slot not found or already booked'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def cancel_slot_by_appointment_id(self, appointment_id: str) -> Dict[str, Any]:
        """Cancel slot booking by appointment ID"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Find the slot with this appointment ID
            slot_query = {
                'types.slots.appointment_id': appointment_id,
                'types.slots.is_booked': True
            }
            
            # Update the slot to make it available again
            result = self.collection.update_one(
                slot_query,
                {
                    '$set': {
                        'types.$[type].slots.$[slot].is_booked': False,
                        'types.$[type].slots.$[slot].patient_id': None,
                        'types.$[type].slots.$[slot].appointment_id': None,
                        'types.$[type].slots.$[slot].cancellation_reason': 'Appointment deleted by patient',
                        'types.$[type].slots.$[slot].booking_timestamp': None,
                        'updated_at': datetime.utcnow()
                    }
                },
                array_filters=[
                    {'type.type': {'$exists': True}},
                    {'slot.appointment_id': appointment_id}
                ]
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Slot made available after appointment deletion',
                    'appointment_id': appointment_id
                }
            else:
                return {
                    'success': False,
                    'error': 'No slot found with this appointment ID'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def update_availability(self, availability_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update availability document"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Add updated timestamp
            updates['updated_at'] = datetime.utcnow()
            
            # Update availability
            result = self.collection.update_one(
                {'availability_id': availability_id},
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Availability updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Availability not found or no changes made'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def delete_availability(self, availability_id: str) -> Dict[str, Any]:
        """Delete availability document"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Soft delete by setting is_active to False
            result = self.collection.update_one(
                {'availability_id': availability_id},
                {
                    '$set': {
                        'is_active': False,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Availability deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Availability not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def cancel_appointment_slot(self, doctor_id: str, date: str, slot_id: str, appointment_id: str, cancellation_reason: str = "Cancelled by doctor", consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a specific appointment slot and make it available again"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Find and update the specific slot
            match_query = {
                'doctor_id': doctor_id,
                'date': date
            }
            if consultation_type:
                match_query['consultation_type'] = consultation_type

            result = self.collection.update_one(
                match_query,
                {
                    '$set': {
                        'types.$[type].slots.$[slot].is_booked': False,
                        'types.$[type].slots.$[slot].patient_id': None,
                        'types.$[type].slots.$[slot].appointment_id': None,
                        'types.$[type].slots.$[slot].cancellation_reason': cancellation_reason,
                        'types.$[type].slots.$[slot].cancelled_at': datetime.utcnow(),
                        'types.$[type].slots.$[slot].booking_timestamp': None,
                        'updated_at': datetime.utcnow()
                    }
                },
                array_filters=[
                    {'type.type': {'$exists': True}},
                    {'slot.slot_id': slot_id, 'slot.appointment_id': appointment_id, 'slot.is_booked': True}
                ]
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Appointment slot cancelled and made available',
                    'slot_id': slot_id,
                    'appointment_id': appointment_id
                }
            else:
                return {
                    'success': False,
                    'error': 'Slot not found or already cancelled'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_booked_slots_by_date(self, doctor_id: str, date: str, consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all booked slots for a specific date"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Use aggregation to get booked slots
            pipeline = [
                {
                    "$match": {
                        "doctor_id": doctor_id,
                        "date": date,
                        "is_active": True
                    }
                },
            ]

            if consultation_type:
                pipeline[0]["$match"]["consultation_type"] = consultation_type

            pipeline.extend([
                {
                    "$unwind": "$types"
                },
                {
                    "$unwind": "$types.slots"
                },
                {
                    "$match": {
                        "types.slots.is_booked": True
                    }
                },
                {
                    "$project": {
                        "availability_id": 1,
                        "doctor_id": 1,
                        "date": 1,
                        "consultation_type": 1,
                        "appointment_type": "$types.type",
                        "slot_id": "$types.slots.slot_id",
                        "start_time": "$types.slots.start_time",
                        "end_time": "$types.slots.end_time",
                        "patient_id": "$types.slots.patient_id",
                        "appointment_id": "$types.slots.appointment_id",
                        "booking_timestamp": "$types.slots.booking_timestamp",
                        "notes": "$types.slots.notes"
                    }
                }
            ])
            
            booked_slots = list(self.collection.aggregate(pipeline))
            
            # Convert ObjectIds to strings
            for slot in booked_slots:
                if '_id' in slot:
                    slot['_id'] = str(slot['_id'])
            
            return {
                'success': True,
                'booked_slots': booked_slots,
                'total_booked': len(booked_slots)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def cancel_all_appointments_for_date(self, doctor_id: str, date: str, cancellation_reason: str = "Full day cancelled by doctor", consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all appointments for a specific date and make all slots available"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Find the availability document for this date
            find_query = {
                'doctor_id': doctor_id,
                'date': date,
                'is_active': True
            }
            if consultation_type:
                find_query['consultation_type'] = consultation_type

            availability_doc = self.collection.find_one(find_query)
            
            if not availability_doc:
                return {
                    'success': False,
                    'error': 'No availability found for this date'
                }
            
            # Count booked slots before cancellation
            booked_slots_count = 0
            cancelled_appointments = []
            
            for appointment_type in availability_doc.get('types', []):
                for slot in appointment_type.get('slots', []):
                    if slot.get('is_booked', False):
                        booked_slots_count += 1
                        cancelled_appointments.append({
                            'slot_id': slot.get('slot_id'),
                            'appointment_id': slot.get('appointment_id'),
                            'patient_id': slot.get('patient_id'),
                            'appointment_type': appointment_type.get('type'),
                            'start_time': slot.get('start_time'),
                            'end_time': slot.get('end_time')
                        })
            
            if booked_slots_count == 0:
                # Soft-disable the day's availability even if no bookings
                self.collection.update_one(
                    {
                        'doctor_id': doctor_id,
                        'date': date,
                        'is_active': True
                    },
                    {
                        '$set': {
                            'is_active': False,
                            'day_cancellation_reason': cancellation_reason,
                            'day_cancelled_at': datetime.utcnow(),
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                return {
                    'success': True,
                    'message': 'No appointments to cancel for this date',
                    'cancelled_count': 0,
                    'cancelled_appointments': []
                }
            
            # Cancel all booked slots for this date and soft-disable the day
            match_query = {
                'doctor_id': doctor_id,
                'date': date,
                'is_active': True
            }
            if consultation_type:
                match_query['consultation_type'] = consultation_type

            result = self.collection.update_one(
                match_query,
                {
                    '$set': {
                        'types.$[].slots.$[slot].is_booked': False,
                        'types.$[].slots.$[slot].patient_id': None,
                        'types.$[].slots.$[slot].appointment_id': None,
                        'types.$[].slots.$[slot].cancellation_reason': cancellation_reason,
                        'types.$[].slots.$[slot].cancelled_at': datetime.utcnow(),
                        'types.$[].slots.$[slot].booking_timestamp': None,
                        'types.$[].available_slots_count': '$types.$[].total_slots_count',
                        'is_active': False,
                        'day_cancellation_reason': cancellation_reason,
                        'day_cancelled_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                },
                array_filters=[
                    {'slot.is_booked': True}
                ]
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': f'All appointments cancelled for {date}',
                    'cancelled_count': booked_slots_count,
                    'cancelled_appointments': cancelled_appointments,
                    'availability_id': availability_doc.get('availability_id')
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to cancel appointments'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def get_date_appointment_summary(self, doctor_id: str, date: str, consultation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of all appointments for a specific date"""
        try:
            self._update_collection()
            
            if self.collection is None:
                return {
                    'success': False,
                    'error': 'Database not connected'
                }
            
            # Find the availability document for this date
            find_query = {
                'doctor_id': doctor_id,
                'date': date,
                'is_active': True
            }
            if consultation_type:
                find_query['consultation_type'] = consultation_type

            availability_doc = self.collection.find_one(find_query)
            
            if not availability_doc:
                return {
                    'success': False,
                    'error': 'No availability found for this date'
                }
            
            # Analyze appointments by type
            appointment_summary = {}
            total_booked = 0
            total_available = 0
            total_slots = 0
            
            for appointment_type in availability_doc.get('types', []):
                type_name = appointment_type.get('type')
                booked_count = 0
                available_count = 0
                
                for slot in appointment_type.get('slots', []):
                    total_slots += 1
                    if slot.get('is_booked', False):
                        booked_count += 1
                        total_booked += 1
                    else:
                        available_count += 1
                        total_available += 1
                
                appointment_summary[type_name] = {
                    'booked_slots': booked_count,
                    'available_slots': available_count,
                    'total_slots': booked_count + available_count,
                    'duration_mins': appointment_type.get('duration_mins'),
                    'price': appointment_type.get('price')
                }
            
            return {
                'success': True,
                'date': date,
                'doctor_id': doctor_id,
                'consultation_type': availability_doc.get('consultation_type'),
                'work_hours': availability_doc.get('work_hours'),
                'appointment_summary': appointment_summary,
                'totals': {
                    'total_booked': total_booked,
                    'total_available': total_available,
                    'total_slots': total_slots
                },
                'availability_id': availability_doc.get('availability_id')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
