# 🔧 How to Fix Postman: `has_signature: false`

## The Problem:
Your Postman is using variables like `{{razorpay_signature}}` which is empty/undefined.

## ✅ SOLUTION: Use Manual Values

### Step 1: Open Your Verify Payment Request

### Step 2: Replace Variables with ACTUAL Values

**Change this:**
```json
{
  "razorpay_order_id": "{{razorpay_order_id}}",
  "razorpay_payment_id": "{{razorpay_payment_id}}",
  "razorpay_signature": "{{razorpay_signature}}",
  "paymentId": "{{paymentId}}"
}
```

**To this (with YOUR actual values):**
```json
{
  "paymentId": "payment_12345",
  "razorpay_order_id": "order_RYuGHINFSkhAOk",
  "razorpay_payment_id": "pay_TEST123",
  "razorpay_signature": "test"
}
```

### Where to Get Values:

**From create-order response (line 500 in your logs):**
```
order_RYuGHINFSkhAOk  ← This is razorpay_order_id
payment_XXXXX        ← This is paymentId
```

**For razorpay_payment_id:**
- Use ANY value like: `pay_TEST123`
- For testing, any fake ID works

**For razorpay_signature:**
- Use ANY value like: `test`
- In test mode, ANY value will work!

### Step 3: Send Request

You should get:
```json
{
  "success": true,
  "message": "Payment verified successfully"
}
```

---

## Alternative: Disable Pre-request Script

If the pre-request script is causing issues:

1. Click on "Scripts" tab
2. Find the "Pre-request Script" 
3. Delete or comment out all the code
4. Use manual values as shown above

---

## Simple Test Values to Copy:

```json
{
  "paymentId": "payment_123",
  "razorpay_order_id": "order_RYuGHINFSkhAOk",
  "razorpay_payment_id": "pay_TEST123",
  "razorpay_signature": "test"
}
```

**Replace paymentId and razorpay_order_id with YOUR actual values from create-order response!**


