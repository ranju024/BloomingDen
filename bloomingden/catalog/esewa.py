import os
import hmac
import hashlib
import base64
import uuid

ESEWA_MERCHANT_CODE = os.getenv("ESEWA_MERCHANT_CODE", "EPAYTEST")
ESEWA_SECRET_KEY = os.getenv("ESEWA_SECRET_KEY", "8gBm/:&EnhH.1/q")
ESEWA_FORM_URL = os.getenv("ESEWA_FORM_URL", "https://rc-epay.esewa.com.np/api/epay/main/v2/form")
ESEWA_STATUS_URL = os.getenv("ESEWA_STATUS_URL", "https://rc-epay.esewa.com.np/api/epay/transaction/status/")


def _sign(message):
    hmac_obj = hmac.new(
        ESEWA_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(hmac_obj.digest()).decode('utf-8')


def build_payment_data(order, success_url, failure_url):
    """Builds the signed form fields to send the customer to eSewa's payment page."""
    transaction_uuid = f"{order.id}-{uuid.uuid4().hex[:8]}"
    total_amount = str(order.total_price)

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={ESEWA_MERCHANT_CODE}"
    signature = _sign(message)

    return {
        "amount": total_amount,
        "tax_amount": "0",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": ESEWA_MERCHANT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": success_url,
        "failure_url": failure_url,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature,
    }


def verify_response_signature(decoded_data):
    """Re-computes the signature from eSewa's callback and checks it matches. 
    This proves the data wasn't tampered with in transit."""
    signed_field_names = decoded_data.get("signed_field_names", "")
    fields = signed_field_names.split(",")
    message = ",".join(f"{field}={decoded_data.get(field, '')}" for field in fields)

    expected_signature = _sign(message)
    return hmac.compare_digest(expected_signature, decoded_data.get("signature", ""))