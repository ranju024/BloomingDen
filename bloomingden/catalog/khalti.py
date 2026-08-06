import os
import requests

KHALTI_SECRET_KEY = os.getenv("KHALTI_SECRET_KEY", "")
KHALTI_BASE_URL = os.getenv("KHALTI_BASE_URL", "https://dev.khalti.com/api/v2")

def initiate_payment(order, return_url, website_url):
    """Asks Khalti to start a payment session. Returns dict with 'pidx' and 'payment_url'. """
    url = f"{KHALTI_BASE_URL}/epayment/initiate/"
    headers = {
        "Authorization": f"key {KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "return_url": return_url,
        "website_url": website_url,
        "amount": int(order.total_price * 100), # Khalti expects paisa, not rupees
        "purchase_order_id": f"order-{order.id}",
        "purchase_order_name": f"BloomingDen Order #{order.id}",
        "customer_info": {
            "name": order.name,
            "phone": order.phone,
        }
    }
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def verify_payment(pidx):
    """Asks Khalti directly whether this payment actually completed.
    Returns dict with 'status', 'total_amount'. """
    url = f"{KHALTI_BASE_URL}/epayment/lookup/"
    headers = {
        "Authorization": f"key {KHALTI_SECRET_KEY}",
        "Content-Type": "application/json", 
    }
    response = requests.post(url, json={"pidx": pidx}, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()