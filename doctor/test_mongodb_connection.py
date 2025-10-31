"""
Test MongoDB Atlas Connection
This script helps diagnose MongoDB connection issues
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    """Test MongoDB connection with detailed diagnostics"""
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    
    # Get connection details from environment
    mongodb_uri = os.environ.get('MONGO_URI')
    database_name = os.environ.get('DB_NAME')
    
    if not mongodb_uri:
        print("❌ MONGO_URI environment variable not set!")
        print("\n📝 Please create a .env file in the doctor folder with:")
        print("   MONGO_URI=mongodb+srv://ramya:XxFn6n0NXx0wBplV@cluster0.c1g1bm5.mongodb.net")
        print("   DB_NAME=doctors_db")
        return False
    
    if not database_name:
        print("❌ DB_NAME environment variable not set!")
        print("\n📝 Please add to your .env file:")
        print("   DB_NAME=doctors_db")
        return False
    
    print(f"\n🔍 Connection URI: {mongodb_uri[:50]}...")
    print(f"🔍 Database Name: {database_name}")
    
    try:
        print("\n🔄 Attempting to connect to MongoDB Atlas...")
        
        # Create client with extended timeouts
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            socketTimeoutMS=60000,
            retryWrites=True,
            retryReads=True
        )
        
        # Test connection
        print("🔄 Testing connection...")
        result = client.admin.command('ping')
        print(f"✅ Connection successful! Ping response: {result}")
        
        # Test database access
        db = client[database_name]
        print(f"✅ Database '{database_name}' accessible")
        
        # List collections
        collections = db.list_collection_names()
        print(f"✅ Found {len(collections)} collections: {collections}")
        
        # Close connection
        client.close()
        print("\n✅ MongoDB connection test PASSED!")
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"\n❌ Server selection timeout: {e}")
        print("\n🔍 Possible causes:")
        print("   1. Your IP address is not whitelisted in MongoDB Atlas")
        print("   2. Network connectivity issues")
        print("   3. MongoDB Atlas cluster is paused or stopped")
        print("\n📝 How to fix:")
        print("   1. Go to MongoDB Atlas Dashboard")
        print("   2. Click 'Network Access' → 'Add IP Address'")
        print("   3. Add '0.0.0.0/0' (allow all) for testing")
        print("   4. Or add your specific IP address")
        return False
        
    except ConnectionFailure as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n🔍 Possible causes:")
        print("   1. Incorrect connection string")
        print("   2. Network firewall blocking MongoDB")
        print("   3. VPN causing connectivity issues")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env file")
    except ImportError:
        print("⚠️ python-dotenv not installed. Using system environment variables.")
    
    success = test_mongodb_connection()
    
    if not success:
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Create a .env file in the doctor folder")
        print("2. Add your MongoDB connection string")
        print("3. Whitelist your IP in MongoDB Atlas")
        print("4. Run this test again")
        sys.exit(1)
    else:
        sys.exit(0)
