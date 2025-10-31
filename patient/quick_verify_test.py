"""
Quick test script to verify payment without needing real Razorpay values
Run this to generate test signature and verify payment
"""
import requests
import hmac
import hashlib
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://localhost:5002"

# Your current order details
PAYMENT_ID = "69019a164222a721740d4e45"
ORDER_ID = "order_RZ9wgwmPRyDjUw"
SECRET_KEY = "OBW4kWXbw4x0FklEagcWKfnw"

def generate_test_signature():
    """Generate a test signature for testing"""
    # Use a test payment ID
    test_payment_id = "pay_TEST123456789"
    
    # Create signature
    message = f"{ORDER_ID}|{test_payment_id}"
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return test_payment_id, signature

def test_verify_payment():
    """Test payment verification with test values"""
    print("=" * 60)
    print("Payment Verification Test")
    print("=" * 60)
    print()
    
    # Get JWT token first (you need to replace this with actual login)
    jwt_token = input("Enter your JWT token (from login): ").strip()
    if not jwt_token:
        print("❌ JWT token required")
        return
    
    # Generate test signature
    test_payment_id, signature = generate_test_signature()
    
    print(f"Order ID: {ORDER_ID}")
    print(f"Payment ID: {test_payment_id}")
    print(f"Signature: {signature}")
    print()
    
    # Prepare request
    url = f"{BASE_URL}/payments/verify-payment"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "paymentId": PAYMENT_ID,
        "razorpay_order_id": ORDER_ID,
        "razorpay_payment_id": test_payment_id,
        "razorpay_signature": signature
    }
    
    print("Sending verification request...")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Note: You need to enable ALLOW_TEST_MODE=true in .env for this to work
    print("⚠️  IMPORTANT: Add ALLOW_TEST_MODE=true to your .env file first!")
    print()
    test_verify_payment()

