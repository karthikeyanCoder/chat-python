# Payment Module - Postman Testing Guide

## 🚀 Quick Start

### Step 1: Create Order (Test Successfully)

**Endpoint:** `POST http://localhost:5002/payments/create-order`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Body:**
```json
{
  "userName": "test_user",
  "amount": 50000,
  "currency": "INR",
  "plan": "1_year_premium"
}
```

**Expected Response:**
```json
{
  "success": true,
  "order": {
    "id": "order_ABC123",
    "amount": 50000,
    "currency": "INR",
    "receipt": "receipt_1234567890"
  },
  "paymentId": "payment_123"
}
```

**Save the `order.id` value for Step 2!**

---

## ⚠️ Step 2: Verify Payment (PROBLEM - Signature Issue)

**Endpoint:** `POST http://localhost:5002/payments/verify-payment`

**Headers:**
```
Authorization: Bearer <same_token>
Content-Type: application/json
```

**Body (NEEDS CORRECT SIGNATURE):**
```json
{
  "paymentId": "payment_123",
  "razorpay_order_id": "order_ABC123",
  "razorpay_payment_id": "pay_XYZ789",
  "razorpay_signature": "generated_signature_here"
}
```

### 🔴 THE PROBLEM

Your verification fails because:
1. You need a **REAL payment ID** from Razorpay (only created during actual payment)
2. The signature must match Razorpay's format exactly

---

## ✅ SOLUTION: Test Verification

### Option A: Generate Test Signature (Recommended)

Use the helper script to generate a valid signature:

```bash
cd patient
python -c "
import sys
sys.path.insert(0, 'app/modules/payments')
from generate_signature import generate_signature
import os
from dotenv import load_dotenv

load_dotenv('env.example')

order_id = 'order_ABC123'  # Your order ID from Step 1
payment_id = 'pay_TEST123'  # Test payment ID
signature = generate_signature(order_id, payment_id)

print(f'Signature: {signature}')
print(f'Use this in Postman:')
print(f'{{')
print(f'  \"razorpay_signature\": \"{signature}\"')
print(f'}}')
"
```

### Option B: Use Static Test Data

For **local testing without real payment**, you can:

1. **Mock the verification temporarily:**

Edit `patient/app/modules/payments/services.py` line 217-257:

```python
def verify_payment_service(...):
    # TEMPORARY: Allow local testing without real signature
    if os.getenv("ALLOW_TEST_MODE") == "true":
        print("[TEST MODE] Skipping signature verification")
        
        payment_doc = _repo.find_by_id_or_order_id(payment_id, razorpay_order_id)
        if not payment_doc:
            return jsonify({"success": False, "message": "Payment record not found"}), 404
        
        # Just update status to paid
        update_data = {
            "status": "paid",
            "razorpayPaymentId": razorpay_payment_id,
            "validityStartDate": datetime.utcnow(),
            "validityEndDate": datetime.utcnow() + timedelta(days=365),
        }
        _repo.update_payment_by_id(payment_doc["_id"], update_data)
        
        return jsonify({"success": True, "message": "Payment verified (TEST MODE)"})
    
    # Normal verification...
```

Add to `.env`:
```
ALLOW_TEST_MODE=true
```

---

## 📋 Complete Postman Collection

### Environment Variables Setup

Create new environment in Postman:

```json
{
  "base_url": "http://localhost:5002",
  "token": "<your_jwt_token>"
}
```

### Collection JSON

```json
{
  "info": {
    "name": "Payment Module Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Create Order",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Authorization", "value": "Bearer {{token}}"},
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"userName\": \"test_user\",\n  \"amount\": 50000,\n  \"currency\": \"INR\",\n  \"plan\": \"1_year_premium\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/payments/create-order",
          "host": ["{{base_url}}"],
          "path": ["payments", "create-order"]
        }
      }
    },
    {
      "name": "2. Verify Payment",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Authorization", "value": "Bearer {{token}}"},
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"paymentId\": \"payment_123\",\n  \"razorpay_order_id\": \"order_ABC\",\n  \"razorpay_payment_id\": \"pay_XYZ\",\n  \"razorpay_signature\": \"test_signature\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/payments/verify-payment",
          "host": ["{{base_url}}"],
          "path": ["payments", "verify-payment"]
        }
      }
    },
    {
      "name": "3. Get Razorpay Key",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/payments/razorpay-key"
        }
      }
    },
    {
      "name": "4. Payment History",
      "request": {
        "method": "GET",
        "header": [
          {"key": "Authorization", "value": "Bearer {{token}}"}
        ],
        "url": {
          "raw": "{{base_url}}/payments/history?username=test_user"
        }
      }
    },
    {
      "name": "5. Premium Status",
      "request": {
        "method": "GET",
        "header": [
          {"key": "Authorization", "value": "Bearer {{token}}"}
        ],
        "url": {
          "raw": "{{base_url}}/payments/premium-status?username=test_user"
        }
      }
    },
    {
      "name": "6. Payments Health",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/payments/health"
        }
      }
    }
  ]
}
```

---

## 🧪 Testing Workflow

1. **Get JWT Token First:**
   ```
   POST http://localhost:5002/signup
   {
     "email": "test@example.com",
     "password": "Test1234!"
   }
   ```
   OR
   ```
   POST http://localhost:5002/login
   {
     "email": "test@example.com",
     "password": "Test1234!"
   }
   ```

2. **Test Create Order** ✅

3. **Test Verify Payment** 
   - If using test mode, it should work
   - If using real mode, need actual Razorpay payment

4. **Test History** - Should show created payment

5. **Test Premium Status** - Should show active premium

---

## 🐛 Common Issues

### Issue: "Signature mismatch"
**Cause:** The signature doesn't match Razorpay's expected format

**Solution:** Use test mode or generate proper signature

### Issue: "Payment record not found"
**Cause:** The paymentId doesn't exist in database

**Solution:** Use the `paymentId` returned from create-order

### Issue: "Razorpay keys not configured"
**Cause:** Missing RAZORPAY_KEY_SECRET in .env

**Solution:** Add to `.env`:
```
RAZORPAY_KEY_SECRET=your_secret_key
```

---

## 📝 Notes

- **Real payment verification** requires actual Razorpay payment flow
- **Test mode** allows local testing without real payment
- **Signature** must be generated server-side for security
- All endpoints require JWT token (except `/razorpay-key`)

