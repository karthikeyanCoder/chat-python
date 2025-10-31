"""
Simplified Flask app for testing nurse creation endpoint
"""

from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

# In-memory storage
doctors = {}
nurses = {}

def get_test_token(user_id, role='doctor'):
    """Generate a test JWT token"""
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'data': {
            'user_id': user_id,
            'email': f"{user_id}@test.com",
            'role': role
        }
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Create a test doctor
test_doctor = {
    'id': 'test123',
    'email': 'doctor@test.com',
    'password': 'password123',
    'role': 'doctor'
}
doctors[test_doctor['id']] = test_doctor

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Find doctor by email
    doctor = next((d for d in doctors.values() if d['email'] == email), None)
    
    if doctor and doctor['password'] == password:
        token = get_test_token(doctor['id'], 'doctor')
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': doctor['id'],
                'email': doctor['email'],
                'role': 'doctor'
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/nurses', methods=['POST'])
def create_nurse():
    """Create nurse endpoint"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify token
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = payload['data']
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Check role
        if current_user['role'] != 'doctor':
            return jsonify({
                'error': 'Permission denied',
                'details': f"Only doctors can create nurse accounts. Your role is: {current_user.get('role', 'unknown')}"
            }), 403
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'details': 'Request body is missing or invalid JSON'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'details': f"The following fields are required: {', '.join(missing_fields)}",
                'required_fields': required_fields
            }), 400
        
        # Create nurse (in memory)
        nurse_id = f"nurse_{len(nurses) + 1}"
        nurse = {
            'nurse_id': nurse_id,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'doctor_id': current_user['user_id'],
            'created_at': datetime.now().isoformat()
        }
        nurses[nurse_id] = nurse
        
        # Generate temporary password
        temp_password = 'nurse123'  # In real app, generate random password
        
        return jsonify({
            'success': True,
            'message': 'Nurse created successfully',
            'nurse': nurse,
            'temporary_password': temp_password
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting test server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)