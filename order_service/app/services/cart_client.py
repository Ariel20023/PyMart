import os
import requests

from fastapi import HTTPException


CART_SERVICE_URL = os.getenv("CART_SERVICE_URL","http://cart_service:8003")


def get_cart(authorization: str):#מביא את העגלה הנוכחית של המשתמש
    try:
        response = requests.get(f"{CART_SERVICE_URL}/cart",headers={"Authorization": authorization},timeout=10
        )

    except requests.RequestException:#שגיאה תקשורת
        raise HTTPException(status_code=503,detail="Cart service is unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400,detail="Could not retrieve cart"
        )

    return response.json()


def clear_cart(authorization: str):#מנקה עגלה אחרי הזמנה שמצליחה
    try:
        response = requests.delete(f"{CART_SERVICE_URL}/cart",headers={"Authorization": authorization},timeout=10
        )

    except requests.RequestException:
        raise HTTPException(status_code=503,detail="Cart service is unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500,detail="Could not clear cart"
        )