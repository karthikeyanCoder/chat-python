"""
Quick script to check if a patient exists in MongoDB
"""
import os
import sys
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get MongoDB connection details
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "patients_db")
collection_name = os.getenv("Patient_COLLECTION_NAME") or os.getenv("COLLECTION_NAME", "Patient_test")

# Email to search for
email_to_find = "umaperiasamy4@gmail.com"

try:
    print(f"[*] Connecting to MongoDB...")
    # Show full URI but mask password
    if "@" in mongo_uri:
        uri_parts = mongo_uri.split("@")
        if len(uri_parts) == 2:
            user_pass = uri_parts[0].split("://")[1] if "://" in uri_parts[0] else uri_parts[0]
            if ":" in user_pass:
                user, _ = user_pass.split(":", 1)
                masked_uri = mongo_uri.replace(user_pass, f"{user}:***")
            else:
                masked_uri = mongo_uri
        else:
            masked_uri = mongo_uri
    else:
        masked_uri = mongo_uri
    print(f"    URI: {masked_uri}")
    print(f"    Database: {db_name}")
    print(f"    Collection: {collection_name}")
    print("")
    
    # Connect to MongoDB
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    
    # Test connection
    client.admin.command('ping')
    print("[OK] MongoDB connection successful")
    print("")
    
    # Get database and collection
    db = client[db_name]
    collection = db[collection_name]
    
    # Search for patient by email
    print(f"[*] Searching for patient with email: {email_to_find}")
    print("")
    
    patient = collection.find_one({"email": email_to_find})
    
    if patient:
        print("[OK] PATIENT FOUND!")
        print("")
        print("Patient Details:")
        print(f"  Patient ID: {patient.get('patient_id', 'N/A')}")
        print(f"  Email: {patient.get('email', 'N/A')}")
        print(f"  Username: {patient.get('username', 'N/A')}")
        print(f"  Status: {patient.get('status', 'N/A')}")
        print(f"  Mobile: {patient.get('mobile', 'N/A')}")
        print(f"  Has Password Hash: {'Yes' if patient.get('password_hash') else 'No'}")
        print(f"  Profile Complete: {patient.get('first_name') and patient.get('last_name') and patient.get('date_of_birth')}")
        print("")
        
        # Show relevant fields for login
        print("Login-relevant fields:")
        print(f"  - Email exists: YES")
        print(f"  - Patient ID: {patient.get('patient_id', 'N/A')}")
        print(f"  - Status: {patient.get('status', 'N/A')} {'[Active]' if patient.get('status') == 'active' else '[Not Active]'}")
        print(f"  - Password hash present: {'YES' if patient.get('password_hash') else 'NO'}")
        
        # Also check by patient_id
        if patient.get('patient_id'):
            print("")
            print(f"[*] Can also login with Patient ID: {patient.get('patient_id')}")
    else:
        print("[X] PATIENT NOT FOUND!")
        print("")
        print(f"No patient found with email: {email_to_find}")
        print("")
        print("[*] Searching for similar emails...")
        # Search for partial matches
        all_patients = collection.find({"email": {"$regex": "umaperiasamy", "$options": "i"}})
        similar = list(all_patients)
        if similar:
            print(f"Found {len(similar)} similar email(s):")
            for p in similar:
                print(f"  - {p.get('email')} (Patient ID: {p.get('patient_id', 'N/A')}, Status: {p.get('status', 'N/A')})")
        else:
            print("  No similar emails found")
        
        # Also check total patients
        total = collection.count_documents({})
        print(f"")
        print(f"Total patients in collection: {total}")
    
    client.close()
    
except pymongo.errors.ServerSelectionTimeoutError:
    print("[ERROR] Cannot connect to MongoDB")
    print(f"    URI: {mongo_uri}")
    print("    Please check:")
    print("    1. MongoDB is running")
    print("    2. MONGO_URI is correct in .env file")
    print("    3. Network/Internet connection (for Atlas)")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

