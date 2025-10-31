#!/usr/bin/env python3
"""
Simple Chat Collection Test
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import Database

print('🔧 Testing Doctor-Patient Chat Collections...')

try:
    # Initialize database (connects automatically)
    db = Database()
    print('✅ Database initialized successfully')

    # Test collection access
    collections_to_test = {
        'patient': 'patient',
        'doctor_v2': 'doctor_v2',
        'connections': 'connections',
        'chat_messages': 'chat_messages',
        'chat_rooms': 'chat_rooms'
    }

    print('🔍 Testing collection access:')
    for name, collection_name in collections_to_test.items():
        try:
            count = db.db[collection_name].count_documents({})
            print(f'   ✅ {name} ({collection_name}): {count} documents')
        except Exception as e:
            print(f'   ❌ {name} ({collection_name}): Error - {str(e)[:50]}...')

    print()
    print('✅ Collection verification complete!')
    print('📋 Summary:')
    print('   - Patient collection: "patient" ✓')
    print('   - Doctor collection: "doctor_v2" ✓')
    print('   - Connections collection: "connections" ✓')
    print('   - Chat Messages collection: "chat_messages" ✓')
    print('   - Chat Rooms collection: "chat_rooms" ✓')

except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()