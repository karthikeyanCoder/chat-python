#!/usr/bin/env python3
"""
Simple MongoDB Connection Test Script
Tests connection to MongoDB Atlas
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Test 1: Check if environment variables are loaded
print("=" * 60)
print("Test 1: Environment Variables")
print("=" * 60)
mongo_uri = os.environ.get('MONGO_URI')
db_name = os.environ.get('DB_NAME')

print(f"MONGO_URI: {'✅ Set' if mongo_uri else '❌ Not set'}")
print(f"DB_NAME: {'✅ Set' if db_name else '❌ Not set'}")

if mongo_uri:
    # Mask the password
    if '@' in mongo_uri:
        display_uri = mongo_uri[:mongo_uri.find('@')+1] + '********@' + mongo_uri.split('@')[1]
    else:
        display_uri = mongo_uri
    print(f"URI: {display_uri}")
else:
    print("❌ MONGO_URI not found in environment")
    sys.exit(1)

print()

# Test 2: Import pymongo
print("=" * 60)
print("Test 2: PyMongo Installation")
print("=" * 60)
try:
    import pymongo
    print(f"✅ PyMongo version: {pymongo.__version__}")
except ImportError:
    print("❌ PyMongo not installed. Install with: pip install pymongo")
    sys.exit(1)

print()

# Test 3: DNS Resolution
print("=" * 60)
print("Test 3: DNS Resolution")
print("=" * 60)
import socket
try:
    host = "cluster0.zhrkdmn.mongodb.net"
    socket.gethostbyname(host)
    print(f"✅ DNS resolution successful for {host}")
except socket.gaierror as e:
    print(f"❌ DNS resolution failed: {e}")
    print("   This usually means:")
    print("   - No internet connection")
    print("   - DNS server issues")
    print("   - Firewall blocking DNS requests")
    sys.exit(1)

print()

# Test 4: Try to connect
print("=" * 60)
print("Test 4: MongoDB Connection")
print("=" * 60)
try:
    from pymongo import MongoClient
    
    print(f"Attempting to connect to MongoDB...")
    print(f"Timeout: 10 seconds")
    
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,  # 10 seconds
        connectTimeoutMS=10000
    )
    
    # Try to ping
    result = client.admin.command('ping')
    print(f"✅ Connection successful!")
    print(f"Ping result: {result}")
    
    # Get database list
    db_list = client.list_database_names()
    print(f"✅ Available databases: {len(db_list)}")
    if db_name in db_list:
        print(f"✅ Target database '{db_name}' exists")
    else:
        print(f"⚠️  Target database '{db_name}' not found")
        print(f"Available databases: {db_list[:5]}")
    
    client.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print()
    print("Common issues:")
    print("1. IP not whitelisted in MongoDB Atlas")
    print("2. Firewall blocking connection")
    print("3. Incorrect credentials")
    print("4. Network connectivity issues")
    print()
    print("Solutions:")
    print("- Check MongoDB Atlas Network Access settings")
    print("- Add your IP address to MongoDB Atlas whitelist")
    print("- Check your firewall/antivirus settings")
    sys.exit(1)

print()
print("=" * 60)
print("✅ All tests passed!")
print("=" * 60)

