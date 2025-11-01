"""
Nurse Model - Handles nurse operations with MongoDB
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import bcrypt
import secrets
import string
from bson import ObjectId
from models.database import Database


class NurseModel:
    """Nurse model for MongoDB operations"""
    
    def __init__(self, db: Database = None):
        if db is None:
            self.db = Database()
            self.db.connect()
        else:
            self.db = db
        
        # Check if database connection is valid
        is_connected = getattr(self.db, 'is_connected', False)
        if self.db is not None and self.db.db is not None and is_connected:
            self.nurses_collection = self.db.db.nurses
            # Ensure index on nurse_id for uniqueness
            try:
                self.nurses_collection.create_index('nurse_id', unique=True)
            except Exception as e:
                error_msg = str(e)
                if 'IndexKeySpecsConflict' in error_msg or 'already exists' in error_msg.lower():
                    pass  # Index already exists, that's fine
                else:
                    print(f"⚠️ Warning: Failed to create nurse_id index: {e}")
        else:
            self.nurses_collection = None
            print("⚠️ Warning: Database not connected. NurseModel operating in fallback mode.")
    
    def _hash_password(self, password: str) -> bytes:
        """Hash password using bcrypt"""
        try:
            print(f"\n🔐 Hashing password...")
            # Convert password to bytes
            password_bytes = password.encode('utf-8')
            # Generate salt and hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            print(f"✅ Password hashed successfully. Hash length: {len(hashed)}")
            return hashed
        except Exception as e:
            print(f"❌ Error hashing password: {str(e)}")
            raise
    
    def _generate_random_password(self, length: int = 12) -> str:
        """Generate a random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def _convert_to_dict(self, nurse_doc) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary"""
        if not nurse_doc:
            return None
        
        nurse_dict = {
            'nurse_id': nurse_doc.get('nurse_id', str(nurse_doc['_id'])),
            'name': nurse_doc.get('name', ''),
            'email': nurse_doc.get('email', ''),
            'phone': nurse_doc.get('phone', ''),
            'department': nurse_doc.get('department', ''),
            'shift': nurse_doc.get('shift', ''),
            'assigned_doctor_id': str(nurse_doc.get('assigned_doctor_id', '')),
            'specialization': nurse_doc.get('specialization', ''),
            'experience_years': nurse_doc.get('experience_years', 0),
            'created_at': nurse_doc.get('created_at', ''),
            'updated_at': nurse_doc.get('updated_at', ''),
            'is_active': nurse_doc.get('is_active', True)
        }
        return nurse_dict
    
    def create_nurse(self, data: Dict[str, Any], doctor_id: str) -> Dict[str, Any]:
        """Create a new nurse"""
        try:
            print("\n📝 Creating new nurse...")
            print(f"📧 Email: {data.get('email')}")
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone']
            for field in required_fields:
                if not data.get(field):
                    print(f"❌ Missing field: {field}")
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Check if email already exists
            existing_nurse = self.find_by_email(data['email'])
            if existing_nurse:
                print(f"❌ Email already exists: {data['email']}")
                return {'success': False, 'error': 'Email already exists'}
            
            # Generate unique nurse_id
            try:
                # Find the last nurse with a proper numeric nurse_id format
                last_nurse = self.nurses_collection.find_one(
                    {'nurse_id': {'$regex': '^N\\d+$'}},  # Match Nxxxxx format
                    sort=[('nurse_id', -1)]
                )
                
                if last_nurse and 'nurse_id' in last_nurse:
                    try:
                        # Extract the numeric part and increment
                        last_id = int(last_nurse['nurse_id'][1:])  # Skip the 'N' prefix
                        new_id = last_id + 1
                    except ValueError:
                        new_id = 1
                else:
                    new_id = 1
                
                nurse_id = f'N{new_id:06d}'  # Format: N000001, N000002, etc.
                print(f"✅ Generated nurse_id: {nurse_id}")
            except Exception as e:
                print(f"❌ Error generating nurse_id: {str(e)}")
                return {'success': False, 'error': f'Failed to generate nurse_id: {str(e)}'}
            
            # Handle password
            print("\n🔐 Processing password...")
            password = data.get('password')
            if not password:
                password = self._generate_random_password()
                print("🎲 Generated random password")
            else:
                print("✅ Using provided password")
            
            print(f"📝 Password length: {len(password)}")
            
            # Hash the password
            try:
                # Convert password to bytes and hash it
                password_bytes = password.encode('utf-8')
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(password_bytes, salt)
                print(f"✅ Password hashed successfully")
                print(f"📊 Hash type: {type(password_hash)}")
                print(f"📊 Hash length: {len(password_hash)}")
                print(f"📊 Hash starts with: {password_hash[:7]}")
                
                # Test verification immediately
                verify_test = bcrypt.checkpw(password_bytes, password_hash)
                print(f"🔍 Immediate verification test: {verify_test}")
            except Exception as e:
                print(f"❌ Error hashing password: {str(e)}")
                return {'success': False, 'error': f'Password hashing failed: {str(e)}'}
                
            nurse_doc = {
                'nurse_id': nurse_id,  # Add the generated nurse_id
                'name': data['name'].strip(),
                'email': data['email'].strip().lower(),
                'phone': data['phone'].strip(),
                'password': password_hash,
                'department': data.get('department', ''),
                'shift': data.get('shift', ''),
                'assigned_doctor_id': doctor_id,  # Store the doctor_id as is
                'specialization': data.get('specialization', ''),
                'experience_years': data.get('experience_years', 0),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            # Insert into database
            result = self.nurses_collection.insert_one(nurse_doc)
            
            if result.inserted_id:
                # Get the created nurse
                created_nurse = self.nurses_collection.find_one({'_id': result.inserted_id})
                response = {
                    'success': True,
                    'nurse': self._convert_to_dict(created_nurse),
                    'message': 'Nurse created successfully'
                }
                
                # Include temporary password in response
                if not data.get('password'):
                    response['temporary_password'] = password
                    
                return response
            else:
                return {'success': False, 'error': 'Failed to create nurse'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find nurse by email"""
        try:
            nurse_doc = self.nurses_collection.find_one({'email': email.strip().lower()})
            return self._convert_to_dict(nurse_doc) if nurse_doc else None
        except Exception as e:
            print(f"Error finding nurse by email: {e}")
            return None
    
    def find_by_id(self, nurse_id: str) -> Optional[Dict[str, Any]]:
        """Find nurse by ID"""
        try:
            if not ObjectId.is_valid(nurse_id):
                return None
            
            nurse_doc = self.nurses_collection.find_one({'_id': ObjectId(nurse_id)})
            return self._convert_to_dict(nurse_doc) if nurse_doc else None
        except Exception as e:
            print(f"Error finding nurse by ID: {e}")
            return None
    
    def list_nurses_by_doctor(self, doctor_id: str) -> Dict[str, Any]:
        """List all nurses assigned to a doctor"""
        try:
            nurses = []
            cursor = self.nurses_collection.find({
                'assigned_doctor_id': doctor_id,
                'is_active': True
            })
            
            for nurse_doc in cursor:
                nurses.append(self._convert_to_dict(nurse_doc))
            
            return {
                'success': True,
                'nurses': nurses,
                'total_count': len(nurses)
            }
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def reset_password(self, nurse_id: str, new_password: str = None) -> Dict[str, Any]:
        """Reset nurse password"""
        try:
            print(f"\n🔄 Attempting to reset password for nurse ID: {nurse_id}")
            
            # Get nurse details first
            nurse_result = self.get_nurse_by_id(nurse_id)
            if not nurse_result['success']:
                print(f"❌ Failed to find nurse: {nurse_result['error']}")
                return {'success': False, 'error': 'Invalid nurse ID'}
                
            # Get the nurse document for updating
            nurse = self.nurses_collection.find_one({'nurse_id': nurse_id})
            if not nurse and ObjectId.is_valid(nurse_id):
                nurse = self.nurses_collection.find_one({'_id': ObjectId(nurse_id)})
                
            print(f"✅ Found nurse: {nurse.get('email')}")
            
            # Generate new password if not provided
            if not new_password:
                new_password = self._generate_random_password()
                print("🎲 Generated random password")
            else:
                print("✅ Using provided password")
            
            # Update password in database
            result = self.nurses_collection.update_one(
                {'_id': nurse['_id']},
                {
                    '$set': {
                        'password': self._hash_password(new_password),
                        'updated_at': datetime.now().isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Password reset successfully',
                    'new_password': new_password
                }
            else:
                return {'success': False, 'error': 'Failed to reset password'}
                
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verify nurse password - basic boolean response"""
        try:
            print(f"\n🔍 Starting password verification for email: {email}")
            
            # Find the nurse
            nurse_doc = self.nurses_collection.find_one({'email': email.strip().lower()})
            if not nurse_doc:
                print("❌ Nurse not found in database")
                return False
            
            print("✅ Found nurse in database")
            
            # Get stored password hash
            stored_hash = nurse_doc.get('password')
            if not stored_hash:
                print("❌ No password hash found in nurse document")
                return False
                
            print(f"💾 Retrieved stored hash:")
            print(f"   Type: {type(stored_hash)}")
            print(f"   Length: {len(stored_hash) if stored_hash else 0}")
            print(f"   First few bytes: {stored_hash[:10] if stored_hash else None}")
            
            try:
                # Ensure password is in bytes
                if isinstance(password, str):
                    password = password.encode('utf-8')
                    print(f"✅ Converted input password to bytes. Length: {len(password)}")
                
                # Ensure stored_hash is in bytes
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                    print("✅ Converted stored hash from string to bytes")
                
                # Verify the password
                print("� Attempting bcrypt password verification...")
                result = bcrypt.checkpw(password, stored_hash)
                print(f"✨ Password verification result: {result}")
                return result
                
            except Exception as e:
                print(f"❌ Error during password verification: {str(e)}")
                print(f"   Error type: {type(e)}")
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error in verify_password: {str(e)}")
            print(f"   Error type: {type(e)}")
            return False

    def verify_nurse_password(self, email: str, password: str) -> Dict[str, Any]:
        """Verify nurse password and return nurse details if successful"""
        try:
            nurse_doc = self.nurses_collection.find_one({'email': email.strip().lower()})
            if not nurse_doc:
                return {'success': False, 'error': 'Nurse not found'}
            
            stored_hash = nurse_doc.get('password')
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return {
                    'success': True,
                    'nurse_id': nurse_doc.get('nurse_id', str(nurse_doc['_id'])),
                    'message': 'Password verified successfully'
                }
            return {'success': False, 'error': 'Invalid password'}
            
        except Exception as e:
            print(f"Error verifying nurse password: {e}")
            return {'success': False, 'error': f'Verification error: {str(e)}'}
            
    def get_nurse_by_id(self, nurse_id: str) -> Dict[str, Any]:
        """Get nurse by ID with full details"""
        try:
            print(f"\n🔍 Looking up nurse with ID: {nurse_id}")
            
            # Try to find by nurse_id first (new format)
            nurse_doc = self.nurses_collection.find_one({'nurse_id': nurse_id})
            if nurse_doc:
                print("✅ Found nurse by nurse_id")
            else:
                # If not found and it's a valid ObjectId, try finding by _id (old format)
                if ObjectId.is_valid(nurse_id):
                    print("🔄 Trying lookup by ObjectId")
                    nurse_doc = self.nurses_collection.find_one({'_id': ObjectId(nurse_id)})
                    if nurse_doc:
                        print("✅ Found nurse by ObjectId")
            
            if not nurse_doc:
                print("❌ Nurse not found")
                return {'success': False, 'error': 'Nurse not found'}
            
            nurse_data = {
                'nurse_id': nurse_doc.get('nurse_id', str(nurse_doc['_id'])),
                'email': nurse_doc.get('email'),
                'name': nurse_doc.get('name'),
                'phone': nurse_doc.get('phone'),
                'doctor_id': nurse_doc.get('assigned_doctor_id'),
                'department': nurse_doc.get('department'),
                'shift': nurse_doc.get('shift'),
                'specialization': nurse_doc.get('specialization'),
                'experience_years': nurse_doc.get('experience_years'),
                'is_active': nurse_doc.get('is_active', True)
            }
            
            return {
                'success': True,
                'data': nurse_data
            }
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def delete_by_email(self, email: str, doctor_id: str) -> Dict[str, Any]:
        """Delete nurse by email (only if assigned to the requesting doctor)"""
        try:
            # Find the nurse first
            nurse_doc = self.nurses_collection.find_one({
                'email': email.strip().lower(),
                'assigned_doctor_id': doctor_id
            })
            
            if not nurse_doc:
                return {
                    'success': False, 
                    'error': 'Nurse not found or not assigned to this doctor'
                }
            
            # Delete the nurse
            result = self.nurses_collection.delete_one({
                '_id': nurse_doc['_id']
            })
            
            if result.deleted_count > 0:
                return {
                    'success': True,
                    'message': f'Nurse with email {email} has been deleted'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete nurse'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }