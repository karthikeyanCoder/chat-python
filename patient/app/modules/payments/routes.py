from flask import Blueprint, request, jsonify
from app.core.auth import token_required
from .services import (
    get_razorpay_key_service,
    create_order_service,
    verify_payment_service,
    get_payment_history_service,
    check_premium_status_service,
    payments_health_service,
)
from .schemas import CreateOrderSchema, VerifyPaymentSchema

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/razorpay-key", methods=["GET"])
def get_razorpay_key():
    return get_razorpay_key_service()


@payments_bp.route("/health", methods=["GET"])
def payments_health():
    return payments_health_service()


@payments_bp.route("/create-order", methods=["POST"])
@token_required
def create_order():
    data = request.get_json() or {}
    errors = CreateOrderSchema().validate(data)
    if errors:
        return {"success": False, "errors": errors}, 400

    username = (
        data.get("userName")
        or request.user_data.get("username")
        or request.user_data.get("email")
        or request.user_data.get("patient_id")
    )
    
    # Validate username is not empty
    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required. Provide userName in request body or ensure token contains user data.",
            "details": {
                "userName_from_body": data.get("userName"),
                "user_data_available": bool(request.user_data)
            }
        }), 400
    
    amount = data.get("amount", 50000)
    currency = data.get("currency", "INR")
    plan = data.get("plan", "1_year_premium")
    
    return create_order_service(username, amount, currency, plan)


@payments_bp.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.get_json() or {}
    errors = VerifyPaymentSchema().validate(data)
    if errors:
        return {"success": False, "errors": errors}, 400

    return verify_payment_service(
        payment_id=data["paymentId"],
        razorpay_order_id=data["razorpay_order_id"],
        razorpay_payment_id=data["razorpay_payment_id"],
        razorpay_signature=data["razorpay_signature"],
    )


# Query-param variant
@payments_bp.route("/history", methods=["GET"])
@token_required
def payment_history():
    username = (
        request.args.get("username")
        or request.user_data.get("username")
        or request.user_data.get("email")
        or request.user_data.get("patient_id")
    )
    return get_payment_history_service(username)


# Path-param variant to match original module
@payments_bp.route("/history/<username>", methods=["GET"])
@token_required
def payment_history_by_username(username):
    return get_payment_history_service(username)


# Query-param variant
@payments_bp.route("/premium-status", methods=["GET"])
@token_required
def premium_status():
    username = (
        request.args.get("username")
        or request.user_data.get("username")
        or request.user_data.get("email")
        or request.user_data.get("patient_id")
    )
    return check_premium_status_service(username)


# Path-param variant to match original module
@payments_bp.route("/premium-status/<username>", methods=["GET"])
@token_required
def premium_status_by_username(username):
    return check_premium_status_service(username)
