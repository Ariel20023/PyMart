import os
import requests
from fastapi import HTTPException

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL","http://auth_service:8001")


def get_current_user(authorization: str | None):#בודק אם תוקן תקין ומחזיר יוזר 
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/validate-token",
            headers={"Authorization": authorization},
            timeout=10  #כדי שהמערכת לא תתקע לנצח
        )
    except requests.RequestException:#אם בכלל אי אפשר לגשת 
        raise HTTPException(status_code=503, detail="Auth service is unavailable")

    if response.status_code != 200:#תוקן לא מתקין
        raise HTTPException(status_code=401, detail="Invalid token")

    return response.json()   #מחזיר אמייל ותפקיד(לדוגמא אדמין)