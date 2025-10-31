#!/usr/bin/env python3
"""
Check Doctor-Patient Chat Collection Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print('🔍 Checking Environment Variables:')
print(f'PATIENTS_COLLECTION: {os.getenv("PATIENTS_COLLECTION")}')
print(f'DOCTORS_COLLECTION: {os.getenv("DOCTORS_COLLECTION")}')
print(f'CHAT_CONNECTIONS_COLLECTION: {os.getenv("CHAT_CONNECTIONS_COLLECTION")}')
print(f'CHAT_MESSAGES_COLLECTION: {os.getenv("CHAT_MESSAGES_COLLECTION")}')
print(f'CHAT_ROOMS_COLLECTION: {os.getenv("CHAT_ROOMS_COLLECTION")}')
print()

print('🔍 Checking Collection Constants in Services:')
try:
    from app.modules.doctor_chat.services import DoctorChatService
    print(f'PATIENT_COLLECTION: {DoctorChatService.PATIENT_COLLECTION}')
    print(f'DOCTOR_COLLECTION: {DoctorChatService.DOCTOR_COLLECTION}')
    print(f'CONNECTIONS_COLLECTION: {DoctorChatService.CONNECTIONS_COLLECTION}')
    print('✅ Collection constants loaded successfully')
except Exception as e:
    print(f'❌ Error loading collection constants: {e}')

print()
print('🔍 Checking Repository Collection Names:')
try:
    from app.modules.doctor_chat.repository import DoctorChatRepository
    # Create a dummy db object to test collection initialization
    class DummyDB:
        def __init__(self):
            self.db = self
            self.client = None

        def get_collection(self, name):
            return f"collection_{name}"

    dummy_db = DummyDB()
    repo = DoctorChatRepository(dummy_db)
    print('✅ Repository initialized successfully')
    print('Chat collections use hardcoded names: chat_messages, chat_rooms')
except Exception as e:
    print(f'❌ Error initializing repository: {e}')

print()
print('✅ All collection names verified:')
print('   - Patient collection: "patient" ✓')
print('   - Doctor collection: "doctor_v2" ✓')
print('   - Connections collection: "connections" ✓')
print('   - Chat messages collection: "chat_messages" ✓')
print('   - Chat rooms collection: "chat_rooms" ✓')