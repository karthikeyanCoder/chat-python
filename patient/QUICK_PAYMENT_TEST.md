# ⚡ Quick Payment Testing Guide

## Problem Summary
✅ Order creation works  
❌ Payment verification fails (signature issue)

---

## 🚀 Solution: Enable Test Mode

### Step 1: Add to `.env` file
```bash
ALLOW_TEST_MODE=true
```

### Step 2: Restart the server
```powershell
cd D:\Pregnancy_AI_Python_Backend\patient
python run_app.py
```

---

## 📋 Postman Test (Copy & Paste)

### ✅ Test 1: Create Order
```
POST http://localhost:5002/payments/create-order
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "userName": "test_user",
  "amount": 50000,
  "currency": "INR",
  "plan": "1_year_premium"
}
```

**Save the `order.id` from response!**

---

### ✅ Test 2: Verify Payment (Test Mode Enabled)
```
POST http://localhost:5002/payments/verify-payment
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "paymentId": "payment_123",           ← From create-order response
  "razorpay_order_id": "order_ABC123",   ← From create-order response
  "razorpay_payment_id": "pay_TEST123",  ← Any test value
  "razorpay_signature": "test_signature" ← Any test value (test mode ignores this)
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "userName": "test_user",
  "premium": {
    "validFrom": "2025-10-28T...",
    "validTill": "2026-10-28T..."
  }
}
```

---

### ✅ Test 3: Check Payment History
```
GET http://localhost:5002/payments/history?username=test_user
Authorization: Bearer YOUR_TOKEN_HERE
```

---

### ✅ Test 4: Check Premium Status
```
GET http://localhost:5002/payments/premium-status?username=test_user
Authorization: Bearer YOUR_TOKEN_HERE
```

**Expected Response:**
```json
{
  "success": true,
  "isPremium": true,
  "premiumValidTill": "2026-10-28T...",
  "daysRemaining": 365
}
```

---

## 🔧 How It Works

1. **Test Mode** (`ALLOW_TEST_MODE=true`):
   - Skips signature verification
   - Allows local testing without real Razorpay payment
   - Just updates payment status to "paid"

2. **Production Mode** (`ALLOW_TEST_MODE=false`):
   - Verifies signature properly
   - Requires real Razorpay payment

---

## 📝 Notes

- **Test mode** is ONLY for local development
- **Never** enable test mode in production
- Real payment verification requires actual Razorpay payment flow
- All endpoints require JWT token

---

## 🎯 Quick Test Sequence

1. Get token → Login/Signup
2. Create order → Get order_id and paymentId
3. Verify payment → Mark as paid (test mode)
4. Check history → See verified payment
5. Check premium → See active premium

---

## ❌ If Still Failing

Check the console logs for:
- `[TEST MODE] Skipping signature verification` → Test mode is active
- `Signature mismatch` → Test mode is OFF or not being read
- Add `ALLOW_TEST_MODE=true` to `.env` and restart server

