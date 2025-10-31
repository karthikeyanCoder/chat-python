# Payment Verification Guide - Complete Step-by-Step

## Current Order Details
```json
{
  "paymentId": "69019a164222a721740d4e45",
  "order_id": "order_RZ9wgwmPRyDjUw",
  "amount": 50000,
  "currency": "INR"
}
```

## Method 1: Enable Test Mode (Easiest)

### Step 1: Add to `.env` file
```bash
ALLOW_TEST_MODE=true
```

### Step 2: Restart server
```bash
python run_app.py
```

### Step 3: Call verify-payment with test values
```bash
POST http://localhost:5002/payments/verify-payment
Authorization: Bearer <YOUR_JWT_TOKEN>

{
  "paymentId": "69019a164222a721740d4e45",
  "razorpay_order_id": "order_RZ9wgwmPRyDjUw",
  "razorpay_payment_id": "pay_TEST123",
  "razorpay_signature": "test_signature_12345"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "userName": "Ramya",
  "premium": {
    "validFrom": "2025-10-29T10:07:42.123456",
    "validTill": "2026-10-29T10:07:42.123456"
  }
}
```

---

## Method 2: Generate Valid Signature (Production Testing)

### Step 1: Use the signature generator script
```bash
cd patient
python app/modules/payments/generate_signature.py
```

### Step 2: Enter your details when prompted
```
Order ID: order_RZ9wgwmPRyDjUw
Payment ID: pay_GENERATED_BY_RAZORPAY
```

The script will generate a valid signature for you.

### Step 3: Use the generated signature in verify-payment call

---

## Method 3: Real Razorpay Integration

### Step 1: Frontend Integration
```html
<!-- Include Razorpay Checkout in your HTML -->
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

<script>
var options = {
  "key": "rzp_test_aDbXtWdupge01S",
  "amount": 50000,
  "currency": "INR",
  "order_id": "order_RZ9wgwmPRyDjUw",
  "handler": function (response){
    // response contains razorpay_payment_id and razorpay_signature
    console.log(response);
    
    // Send to your backend
    fetch('/payments/verify-payment', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + JWT_TOKEN,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        paymentId: "69019a164222a721740d4e45",
        razorpay_order_id: response.razorpay_order_id,
        razorpay_payment_id: response.razorpay_payment_id,
        razorpay_signature: response.razorpay_signature
      })
    });
  }
};
var rzp = new Razorpay(options);
rzp.open();
</script>
```

---

## Quick Reference

### ✅ What You Have:
- ✅ `paymentId`: `69019a164222a721740d4e45` (from create-order response)
- ✅ `razorpay_order_id`: `order_RZ9wgwmPRyDjUw` (from create-order response)

### ❌ What You Need:
- ❌ `razorpay_payment_id`: Need from Razorpay Checkout callback
- ❌ `razorpay_signature`: Need from Razorpay Checkout callback

### 🔧 For Testing:
Use test values + enable `ALLOW_TEST_MODE=true`

---

## Complete Test Flow

```bash
# 1. Login
POST http://localhost:5002/login
{
  "login_identifier": "your_email@example.com",
  "password": "your_password"
}
# Save JWT token

# 2. Create Order
POST http://localhost:5002/payments/create-order
Authorization: Bearer <JWT>
{
  "userName": "Ramya",
  "amount": 50000,
  "currency": "INR",
  "plan": "1_year_premium"
}
# Save paymentId and order_id

# 3. Verify Payment (Test Mode)
# First: Add ALLOW_TEST_MODE=true to .env and restart
POST http://localhost:5002/payments/verify-payment
Authorization: Bearer <JWT>
{
  "paymentId": "69019a164222a721740d4e45",
  "razorpay_order_id": "order_RZ9wgwmPRyDjUw",
  "razorpay_payment_id": "pay_TEST123",
  "razorpay_signature": "test_signature_12345"
}

# 4. Check Premium Status
GET http://localhost:5002/payments/premium-status/Ramya
Authorization: Bearer <JWT>

# 5. Get Payment History
GET http://localhost:5002/payments/history/Ramya
Authorization: Bearer <JWT>
```

---

## Environment Variables Needed

### Required (.env file):
```bash
RAZORPAY_KEY_ID=rzp_test_aDbXtWdupge01S
RAZORPAY_KEY_SECRET=OBW4kWXbw4x0FklEagcWKfnw

# Enable test mode for development
ALLOW_TEST_MODE=true
```

---

## Troubleshooting

### Issue: "Payment verification failed - Signature mismatch"
**Solution**: Enable test mode or ensure signature is correctly computed

### Issue: "Missing required payment fields"
**Solution**: Make sure all 4 fields are provided (paymentId, razorpay_order_id, razorpay_payment_id, razorpay_signature)

### Issue: "Payment record not found"
**Solution**: Make sure paymentId matches the one from create-order response

---

## Signature Generation (Manual)

If you need to manually generate a signature:

```python
import hmac
import hashlib

# Your order and payment IDs
order_id = "order_RZ9wgwmPRyDjUw"
payment_id = "pay_GENERATED_BY_RAZORPAY"

# Your secret key
secret = "OBW4kWXbw4x0FklEagcWKfnw"

# Generate signature
message = f"{order_id}|{payment_id}"
signature = hmac.new(
    secret.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()

print(f"Signature: {signature}")
```

---

## Summary

**For Testing**: Use test mode with dummy values
**For Production**: Use real Razorpay Checkout callback values
**For Manual**: Use signature generator or compute yourself

Your current order is ready to verify once you have the payment_id and signature!

