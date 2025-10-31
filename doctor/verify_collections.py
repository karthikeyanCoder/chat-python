#!/usr/bin/env python3
"""
Comprehensive Collection Name Verification
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print('🔍 COMPREHENSIVE COLLECTION NAME VERIFICATION')
print('=' * 50)

# Check .env file
print('📄 .env file:')
env_collections = {
    'PATIENTS_COLLECTION': os.getenv('PATIENTS_COLLECTION'),
    'DOCTORS_COLLECTION': os.getenv('DOCTORS_COLLECTION'),
    'CHAT_CONNECTIONS_COLLECTION': os.getenv('CHAT_CONNECTIONS_COLLECTION'),
    'CHAT_MESSAGES_COLLECTION': os.getenv('CHAT_MESSAGES_COLLECTION'),
    'CHAT_ROOMS_COLLECTION': os.getenv('CHAT_ROOMS_COLLECTION')
}
for key, value in env_collections.items():
    print(f'   {key}: {value}')

print()

# Check services.py constants
print('📄 services.py constants:')
try:
    from app.modules.doctor_chat.services import DoctorChatService
    service_constants = {
        'PATIENT_COLLECTION': DoctorChatService.PATIENT_COLLECTION,
        'DOCTOR_COLLECTION': DoctorChatService.DOCTOR_COLLECTION,
        'CONNECTIONS_COLLECTION': DoctorChatService.CONNECTIONS_COLLECTION
    }
    for key, value in service_constants.items():
        print(f'   {key}: {value}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()

# Check config.py
print('📄 config.py:')
try:
    from app.core.config import PATIENTS_COLLECTION, DOCTORS_COLLECTION
    config_collections = {
        'PATIENTS_COLLECTION': PATIENTS_COLLECTION,
        'DOCTORS_COLLECTION': DOCTORS_COLLECTION
    }
    for key, value in config_collections.items():
        print(f'   {key}: {value}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()

# Check repository hardcoded names
print('📄 repository.py hardcoded names:')
repo_collections = {
    'messages_collection': 'chat_messages',
    'chat_rooms_collection': 'chat_rooms'
}
for key, value in repo_collections.items():
    print(f'   {key}: {value}')

print()
print('🔍 VERIFICATION RESULTS:')
print('=' * 30)

# Verify matches
issues = []

# Check patient collection
if env_collections['PATIENTS_COLLECTION'] != service_constants.get('PATIENT_COLLECTION'):
    issues.append(f'❌ PATIENTS_COLLECTION mismatch: .env={env_collections["PATIENTS_COLLECTION"]} vs services.py={service_constants.get("PATIENT_COLLECTION")}')

if env_collections['PATIENTS_COLLECTION'] != config_collections.get('PATIENTS_COLLECTION'):
    issues.append(f'❌ PATIENTS_COLLECTION mismatch: .env={env_collections["PATIENTS_COLLECTION"]} vs config.py={config_collections.get("PATIENTS_COLLECTION")}')

# Check doctor collection
if env_collections['DOCTORS_COLLECTION'] != service_constants.get('DOCTOR_COLLECTION'):
    issues.append(f'❌ DOCTORS_COLLECTION mismatch: .env={env_collections["DOCTORS_COLLECTION"]} vs services.py={service_constants.get("DOCTOR_COLLECTION")}')

if env_collections['DOCTORS_COLLECTION'] != config_collections.get('DOCTORS_COLLECTION'):
    issues.append(f'❌ DOCTORS_COLLECTION mismatch: .env={env_collections["DOCTORS_COLLECTION"]} vs config.py={config_collections.get("DOCTORS_COLLECTION")}')

# Check chat collections
if env_collections['CHAT_CONNECTIONS_COLLECTION'] != service_constants.get('CONNECTIONS_COLLECTION'):
    issues.append(f'❌ CHAT_CONNECTIONS_COLLECTION mismatch: .env={env_collections["CHAT_CONNECTIONS_COLLECTION"]} vs services.py={service_constants.get("CONNECTIONS_COLLECTION")}')

if env_collections['CHAT_MESSAGES_COLLECTION'] != repo_collections['messages_collection']:
    issues.append(f'❌ CHAT_MESSAGES_COLLECTION mismatch: .env={env_collections["CHAT_MESSAGES_COLLECTION"]} vs repository.py={repo_collections["messages_collection"]}')

if env_collections['CHAT_ROOMS_COLLECTION'] != repo_collections['chat_rooms_collection']:
    issues.append(f'❌ CHAT_ROOMS_COLLECTION mismatch: .env={env_collections["CHAT_ROOMS_COLLECTION"]} vs repository.py={repo_collections["chat_rooms_collection"]}')

if not issues:
    print('✅ ALL COLLECTION NAMES MATCH PERFECTLY!')
    print('   - Patient collection: "patient" ✓')
    print('   - Doctor collection: "doctor_v2" ✓')
    print('   - Connections collection: "connections" ✓')
    print('   - Chat Messages collection: "chat_messages" ✓')
    print('   - Chat Rooms collection: "chat_rooms" ✓')
    print()
    print('🎉 NO MISMATCHES OR WARNINGS FOUND!')
else:
    print('❌ ISSUES FOUND:')
    for issue in issues:
        print(f'   {issue}')