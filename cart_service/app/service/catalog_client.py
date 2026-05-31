import os
import requests
from fastapi import HTTPException

CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL",
    "http://catalog_service:8000"
)


def get_product(product_id: str):#מבקש מוצר
    try:
        response = requests.get(
            f"{CATALOG_SERVICE_URL}/products/{product_id}",
            timeout=10
        )
    except requests.RequestException:#אם אי אפשר בכלל לגשת 
        raise HTTPException(status_code=503, detail="Catalog service is unavailable")

    if response.status_code == 404:#לא נמצא
        raise HTTPException(status_code=404, detail="Product does not exist")

    if response.status_code != 200:#בעיה בשרת
        raise HTTPException(status_code=500, detail="Catalog service error")

    return response.json() #מחזיר את המוצר 