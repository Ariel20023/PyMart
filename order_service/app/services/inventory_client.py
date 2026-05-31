import os
import requests

from fastapi import HTTPException


INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL","http://inventory_service:8005")


def reserve_inventory(items: list, authorization: str):#מבקש לשריין מלאי כלומר לבדוק אם יש מלאי

    try:
        response = requests.post(f"{INVENTORY_SERVICE_URL}/inventory/reserve",json={"items": items},headers={"Authorization": authorization},
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(status_code=503,detail="Inventory service is unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400,detail="Not enough stock")