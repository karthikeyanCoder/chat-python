import os
import hmac
import hashlib
from datetime import datetime, timedelta
from flask import jsonify
import razorpay
import razorpay.errors

from app.core.database import db
from .repository import PaymentsRepository

_repo = PaymentsRepository(db)
_razorpay_client = None


def _get_razorpay_client():
    global _razorpay_client
    if _razorpay_client:
        return _razorpay_client
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    # Log the keys being used (first few chars only for security)
    print(f"[DEBUG] Using Razorpay Key ID: {key_id[:10]}..." if key_id and len(key_id) > 10 else f"[DEBUG] Key ID: {key_id}")
    
    if key_id and key_secret:
        _razorpay_client = razorpay.Client(auth=(key_id, key_secret))
    return _razorpay_client


def get_razorpay_key_service():
    key = os.getenv("RAZORPAY_KEY_ID", "rzp_test_demo_key")
    return jsonify({"success": True, "key": key}), 200


def payments_health_service():
    try:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        # Check if keys are set
        if not key_id or not key_secret:
            return jsonify({
                "success": False,
                "message": "Razorpay keys not configured",
                "has_key_id": bool(key_id),
                "has_key_secret": bool(key_secret),
                "key_id_preview": key_id[:10] + "..." if key_id and len(key_id) > 10 else key_id
            }), 500

        client = _get_razorpay_client()
        if not client:
            return jsonify({
                "success": False, 
                "message": "Payment gateway not configured"
            }), 500

        # Test the client by trying to fetch payment methods (simpler API call)
        try:
            # Try to fetch payment methods to validate credentials
            payment_methods = client.payment_method.all()
            return jsonify({
                "success": True,
                "message": "Payments health OK - Razorpay credentials verified",
                "key_id": key_id[:15] + "..." if len(key_id) > 15 else key_id,
                "has_secret": bool(key_secret),
                "status": "verified"
            }), 200
        except razorpay.errors.BadRequestError as e:
            # Bad credentials
            return jsonify({
                "success": False,
                "message": "Razorpay credentials invalid - BadRequestError",
                "error": str(e),
                "key_id": key_id[:15] + "..." if len(key_id) > 15 else key_id,
                "has_secret": bool(key_secret)
            }), 401
        except Exception as e:
            # Other errors - but credentials might still be valid
            # Don't fail the health check for this, just log it
            print(f"[WARNING] Razorpay health check: {str(e)}")
            return jsonify({
                "success": True,
                "message": "Payments configured (credentials not fully verified)",
                "key_id": key_id[:15] + "..." if len(key_id) > 15 else key_id,
                "has_secret": bool(key_secret),
                "status": "configured",
                "warning": str(e)
            }), 200
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": "Payments health check failed", 
            "error": str(e)
        }), 500


def create_order_service(username: str, amount: int = 50000, currency: str = "INR", plan: str = "1_year_premium"):
    try:
        # Validate username first
        if not username or username.strip() == "":
            return jsonify({
                "success": False,
                "message": "Username is required",
                "details": {
                    "username_provided": username
                }
            }), 400
        
        # Validate keys early for clearer errors
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        if not key_id or not key_secret:
            return jsonify({
                "success": False,
                "message": "Razorpay keys not configured",
                "details": {
                    "has_key_id": bool(key_id),
                    "has_key_secret": bool(key_secret)
                }
            }), 500

        client = _get_razorpay_client()
        if not client:
            return jsonify({"success": False, "message": "Payment gateway not configured"}), 500

        options = {
            "amount": int(amount),
            "currency": currency,
            "receipt": f"receipt_{int(datetime.now().timestamp())}",
            "notes": {"userName": username, "plan": plan},
        }

        # Create order with Razorpay and capture specific errors
        try:
            # Log the request details
            print(f"[DEBUG] Creating Razorpay order with: amount={options['amount']}, currency={options['currency']}, receipt={options['receipt']}")
            rz_order = client.order.create(data=options)
            print(f"[DEBUG] Razorpay order created successfully: {rz_order.get('id')}")
        except razorpay.errors.BadRequestError as e:
            # Razorpay-specific authentication/validation errors
            error_msg = str(e)
            print(f"[ERROR] Razorpay BadRequestError: {error_msg}")
            import traceback
            print(traceback.format_exc())
            return jsonify({
                "success": False,
                "message": "Razorpay order creation failed - Invalid credentials or parameters",
                "error": error_msg,
                "error_type": "BadRequestError",
                "details": {
                    "key_id": key_id[:10] + "..." if key_id else None,
                    "amount": options["amount"],
                    "currency": options["currency"]
                }
            }), 400
        except Exception as e:
            # Other errors
            print(f"[ERROR] Razorpay order creation failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return jsonify({
                "success": False,
                "message": "Razorpay order creation failed",
                "error": str(e),
                "error_type": type(e).__name__
            }), 502

        payment_doc = {
            "userName": username,
            "razorpayOrderId": rz_order["id"],
            "amount": options["amount"],
            "currency": options["currency"],
            "status": "created",
            "gateway": "Razorpay",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

        payment_id = None
        if db.is_connected():
            payment_id = _repo.insert_payment(payment_doc)
        else:
            payment_id = f"payment_{int(datetime.now().timestamp())}"

        return jsonify({
            "success": True,
            "order": {
                "id": rz_order["id"],
                "amount": rz_order["amount"],
                "currency": rz_order["currency"],
                "receipt": rz_order["receipt"],
            },
            "paymentId": payment_id,
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": "Failed to create order", "error": str(e)}), 500


def verify_payment_service(payment_id: str, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    try:
        # Check for test mode (allow testing without real signature)
        allow_test_mode = os.getenv("ALLOW_TEST_MODE", "false").lower() == "true"
        
        print(f"[DEBUG] verify_payment_service called with:")
        print(f"  payment_id: {payment_id}")
        print(f"  razorpay_order_id: {razorpay_order_id}")
        print(f"  razorpay_payment_id: {razorpay_payment_id}")
        print(f"  razorpay_signature: {razorpay_signature}")
        print(f"  ALLOW_TEST_MODE: {allow_test_mode}")

        # Validate inputs (signature can be empty in test mode)
        missing_error = {
            "success": False,
            "message": "Missing required payment fields",
            "details": {
                "has_payment_id": bool(payment_id),
                "has_order_id": bool(razorpay_order_id),
                "has_payment_id_rzp": bool(razorpay_payment_id),
                "has_signature": bool(razorpay_signature)
            }
        }
        
        # Check required fields
        if not payment_id or not razorpay_order_id or not razorpay_payment_id:
            print(f"[ERROR] Missing required fields!")
            return jsonify(missing_error), 400
            
        # Only require signature if not in test mode
        if not allow_test_mode and not razorpay_signature:
            print(f"[ERROR] Signature required but not in test mode!")
            return jsonify(missing_error), 400
        
        secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        if not secret:
            return jsonify({"success": False, "message": "Razorpay secret key not configured"}), 500
        
        body = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        
        print(f"[DEBUG] Verifying payment:")
        print(f"[DEBUG] Order ID: {razorpay_order_id}")
        print(f"[DEBUG] Payment ID: {razorpay_payment_id}")
        print(f"[DEBUG] Expected signature: {expected_signature[:20]}...")
        print(f"[DEBUG] Received signature: {razorpay_signature[:20]}...")
        print(f"[DEBUG] Test mode enabled: {allow_test_mode}")

        payment_doc = None
        if db.is_connected():
            payment_doc = _repo.find_by_id_or_order_id(payment_id, razorpay_order_id)

        if not payment_doc:
            return jsonify({
                "success": False,
                "message": "Payment record not found",
                "details": {
                    "payment_id": payment_id,
                    "razorpay_order_id": razorpay_order_id
                }
            }), 404

        # Skip signature check in test mode
        if not allow_test_mode and expected_signature != razorpay_signature:
            print(f"[ERROR] Signature mismatch!")
            print(f"[ERROR] Expected: {expected_signature}")
            print(f"[ERROR] Got: {razorpay_signature}")
            if db.is_connected():
                _repo.update_payment_by_id(payment_doc["_id"], {"status": "failed", "verification_error": "signature_mismatch"})
            return jsonify({
                "success": False,
                "message": "Payment verification failed - Signature mismatch",
                "details": {
                    "error": "Invalid signature",
                    "order_id": razorpay_order_id,
                    "expected": expected_signature[:20] + "...",
                    "received": razorpay_signature[:20] + "..."
                }
            }), 400
        
        if allow_test_mode:
            print(f"[TEST MODE] Skipping signature verification for testing")

        current_date = datetime.utcnow()
        validity_end = current_date + timedelta(days=365)

        update_data = {
            "razorpayPaymentId": razorpay_payment_id,
            "razorpaySignature": razorpay_signature,
            "status": "paid",
            "validityStartDate": current_date,
            "validityEndDate": validity_end,
        }

        if db.is_connected():
            _repo.update_payment_by_id(payment_doc["_id"], update_data)

        return jsonify({
            "success": True,
            "message": "Payment verified successfully",
            "userName": payment_doc.get("userName"),
            "premium": {"validFrom": current_date.isoformat(), "validTill": validity_end.isoformat()},
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Payment verification failed", "error": str(e)}), 500


def get_payment_history_service(username: str):
    try:
        if db.is_connected():
            items = _repo.list_user_payments(username)
        else:
            items = []
        return jsonify({"success": True, "payments": items}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to fetch payment history", "error": str(e)}), 500


def check_premium_status_service(username: str):
    try:
        if not db.is_connected():
            return jsonify({"success": True, "isPremium": False, "premiumValidTill": None, "daysRemaining": 0}), 200

        latest = _repo.latest_paid(username)
        if not latest:
            return jsonify({"success": True, "isPremium": False, "premiumValidTill": None, "daysRemaining": 0}), 200

        now = datetime.utcnow()
        valid_till = latest.get("validityEndDate")
        is_active = bool(valid_till and valid_till > now)
        days_remaining = (valid_till - now).days if is_active else 0

        return jsonify({
            "success": True,
            "isPremium": is_active,
            "premiumValidTill": valid_till.isoformat() if valid_till else None,
            "daysRemaining": days_remaining,
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to check premium status", "error": str(e)}), 500
