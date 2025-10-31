from marshmallow import Schema, fields, validate


class CreateOrderSchema(Schema):
    userName = fields.Str(required=False)
    amount = fields.Int(required=False, missing=50000)
    currency = fields.Str(required=False, missing="INR", validate=validate.OneOf(["INR"]))
    plan = fields.Str(required=False, missing="1_year_premium")


class VerifyPaymentSchema(Schema):
    paymentId = fields.Str(required=True)
    razorpay_order_id = fields.Str(required=True)
    razorpay_payment_id = fields.Str(required=True)
    razorpay_signature = fields.Str(required=True)
