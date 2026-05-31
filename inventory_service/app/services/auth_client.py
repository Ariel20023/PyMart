import os
import requests

from fastapi import HTTPException


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL","http://auth_service:8001")


def get_current_user(authorization: str | None):#בודק מי המשתמש והאם התוקן תקין

    if not authorization:
        raise HTTPException(status_code=401,
            detail="Missing token"
        )

    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/validate-token",
            headers={"Authorization": authorization},
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(status_code=503,
            detail="Auth service unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401,
            detail="Invalid token"
        )

    return response.json()