import os
import requests

from fastapi import HTTPException


CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL","http://catalog_service:8000")


def get_product(product_id: str):#מביא מוצר מהקטלוג

    try:
        response = requests.get(f"{CATALOG_SERVICE_URL}/products/{product_id}",
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(status_code=503,
            detail="Catalog service unavailable"
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404,
            detail="Product not found"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500,
            detail="Catalog service error"
        )

    return response.json()


def update_product_stock(product_id: str,stock_count: int,authorization: str):#מעדכן את ה stock count

    try:
        response = requests.patch(f"{CATALOG_SERVICE_URL}/products/{product_id}",data={"stock_count": stock_count},
            headers={"Authorization": authorization},
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(status_code=503,
            detail="Catalog service unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500,
            detail="Failed to update stock"
        )