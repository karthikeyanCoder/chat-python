#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick S3 Configuration Test
Run this to verify S3 is properly configured
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="  * 60)
print("S3 Configuration Test")
print("=" * 60)

# Check .env file
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    print("[OK] .env file found")
else:
    print("[ERROR] .env file NOT found")
    sys.exit(1)

# Check AWS credentials
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
s3_bucket = os.getenv('S3_BUCKET_NAME')
s3_enabled = os.getenv('S3_UPLOAD_ENABLED', 'true').lower() == 'true'

print("\nEnvironment Variables:")
print(f"   AWS_ACCESS_KEY_ID: {'[OK] Set' if aws_access_key else '[ERROR] Missing'}")
if aws_access_key:
    print(f"      Value: {aws_access_key[:10]}...{aws_access_key[-4:]}")

print(f"   AWS_SECRET_ACCESS_KEY: {'[OK] Set' if aws_secret_key else '[ERROR] Missing'}")
if aws_secret_key:
    print(f"      Value: {aws_secret_key[:10]}...{aws_secret_key[-4:]}")

print(f"   AWS_REGION: {aws_region or '[ERROR] Missing'}")
print(f"   S3_BUCKET_NAME: {s3_bucket or '[ERROR] Missing'}")
print(f"   S3_UPLOAD_ENABLED: {'[OK] Enabled' if s3_enabled else '[ERROR] Disabled'}")

# Check boto3
print("\nboto3 Library:")
try:
    import boto3
    print("   [OK] boto3 installed")
    print(f"   Version: {boto3.__version__}")
except ImportError:
    print("   [ERROR] boto3 NOT installed")
    print("   Install with: pip install boto3")
    sys.exit(1)

# Test S3 connection
if aws_access_key and aws_secret_key and aws_region and s3_bucket:
    print("\nTesting S3 Connection...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Try to head the bucket
        s3_client.head_bucket(Bucket=s3_bucket)
        print(f"   [OK] Successfully connected to bucket: {s3_bucket}")
        
        # List some objects
        response = s3_client.list_objects_v2(Bucket=s3_bucket, MaxKeys=5)
        if 'Contents' in response:
            print(f"   [INFO] Found {len(response['Contents'])} objects in bucket")
            for obj in response['Contents'][:3]:
                print(f"      - {obj['Key']}")
        else:
            print("   [INFO] Bucket is empty (no objects yet)")
        
    except Exception as e:
        print(f"   [ERROR] Error connecting to S3: {str(e)}")
        sys.exit(1)
else:
    print("\n[WARNING] Cannot test S3 connection - missing credentials")

print("\n" + "=" * 60)
print("[SUCCESS] S3 Configuration Test Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Start backend: python app_mvc.py")
print("2. Check for: [OK] S3 Service ENABLED message")
print("3. Test upload: curl http://localhost:5000/doctor/chat/health")

