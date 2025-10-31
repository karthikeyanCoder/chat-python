"""
Helper script to generate Razorpay payment signature for testing
Run this to generate a test signature for Postman verification testing
"""
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

def generate_signature(order_id: str, payment_id: str, secret_key: str = None) -> str:
    """
    Generate Razorpay signature for payment verification
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        secret_key: Razorpay secret key (defaults to env variable)
    
    Returns:
        SHA256 signature in hex format
    """
    if not secret_key:
        secret_key = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    if not secret_key:
        raise ValueError("RAZORPAY_KEY_SECRET not found in environment")
    
    # Generate signature: order_id|payment_id
    message = f"{order_id}|{payment_id}"
    
    # Create HMAC SHA256 signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def main():
    """Interactive signature generation for testing"""
    print("=" * 60)
    print("Razorpay Payment Signature Generator (for Testing)")
    print("=" * 60)
    print()
    
    secret_key = os.getenv("RAZORPAY_KEY_SECRET", "")
    if not secret_key:
        print("⚠️  WARNING: RAZORPAY_KEY_SECRET not found in environment")
        print("Please add RAZORPAY_KEY_SECRET to your .env file")
        print()
    
    order_id = input("Enter Razorpay Order ID: ").strip()
    payment_id = input("Enter Razorpay Payment ID: ").strip()
    
    if not secret_key:
        secret_key = input("Enter Razorpay Secret Key: ").strip()
    
    if not all([order_id, payment_id, secret_key]):
        print("❌ Error: Order ID, Payment ID, and Secret Key are required")
        return
    
    signature = generate_signature(order_id, payment_id, secret_key)
    
    print()
    print("=" * 60)
    print("Generated Signature:")
    print("=" * 60)
    print()
    print(f"Order ID:     {order_id}")
    print(f"Payment ID:   {payment_id}")
    print(f"Signature:    {signature}")
    print()
    print("=" * 60)
    print("Use this in your Postman verify-payment request:")
    print("=" * 60)
    print()
    print("```json")
    print("{")
    print(f'  "paymentId": "<your_payment_id_from_db>",')
    print(f'  "razorpay_order_id": "{order_id}",')
    print(f'  "razorpay_payment_id": "{payment_id}",')
    print(f'  "razorpay_signature": "{signature}"')
    print("}")
    print("```")
    print()


if __name__ == "__main__":
    main()

