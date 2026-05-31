import os
import requests
from fastapi import Header, HTTPException

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8001")


def require_admin(authorization: str = Header(None)):#בדיקה אם זה אדמין
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/validate-admin",headers={"Authorization": authorization},
            timeout=5
        )
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Auth service is not available")

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid token")#תוקן לא תקין

    if response.status_code == 403:#זה לא אדמין 
        raise HTTPException(status_code=403, detail="only admin")

    if response.status_code != 200:#לא תקין
        raise HTTPException(status_code=500, detail="Auth service error")

    return response.json()
