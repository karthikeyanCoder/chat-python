#!/usr/bin/env python3
"""
Configure AWS S3 Bucket CORS for Web Access
Run this once to enable web browsers to access S3 files
"""
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_s3_cors():
    """Configure CORS policy for S3 bucket"""
    
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'ap-south-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    
    if not all([aws_access_key, aws_secret_key, s3_bucket]):
        print("❌ Missing AWS credentials in .env file")
        return False
    
    print("=" * 60)
    print("Configuring S3 CORS for Web Access")
    print("=" * 60)
    print(f"Bucket: {s3_bucket}")
    print(f"Region: {aws_region}")
    print()
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # CORS configuration for web access
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'HEAD', 'PUT', 'POST', 'DELETE'],
                    'AllowedOrigins': [
                        'http://localhost:*',  # Local development
                        'http://127.0.0.1:*',
                        'http://*.local:*',
                        'https://*.onrender.com',  # Production
                        '*'  # Allow all origins (for testing)
                    ],
                    'ExposeHeaders': [
                        'ETag',
                        'Content-Length',
                        'Content-Type',
                        'x-amz-request-id'
                    ],
                    'MaxAgeSeconds': 3600
                }
            ]
        }
        
        # Apply CORS configuration
        print("🔧 Applying CORS configuration...")
        s3_client.put_bucket_cors(
            Bucket=s3_bucket,
            CORSConfiguration=cors_configuration
        )
        
        print("✅ CORS configuration applied successfully!")
        print()
        
        # Verify CORS configuration
        print("🔍 Verifying CORS configuration...")
        response = s3_client.get_bucket_cors(Bucket=s3_bucket)
        
        print("✅ Current CORS rules:")
        for i, rule in enumerate(response['CORSRules'], 1):
            print(f"\n  Rule {i}:")
            print(f"    Allowed Methods: {', '.join(rule['AllowedMethods'])}")
            print(f"    Allowed Origins: {', '.join(rule['AllowedOrigins'])}")
            print(f"    Allowed Headers: {', '.join(rule['AllowedHeaders'])}")
            if 'ExposeHeaders' in rule:
                print(f"    Expose Headers: {', '.join(rule['ExposeHeaders'])}")
        
        print()
        print("=" * 60)
        print("✅ S3 CORS Configuration Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart your Flask backend")
        print("2. Refresh your Flutter web app")
        print("3. Test image/audio uploads - CORS errors should be gone!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error configuring CORS: {str(e)}")
        return False

if __name__ == '__main__':
    configure_s3_cors()

