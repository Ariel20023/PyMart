import os
import requests
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Query
from elasticsearch import NotFoundError

from app.services.elastic import es


PRODUCTS_INDEX = os.getenv("PRODUCTS_INDEX", "products")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL","http://auth_service:8001")

STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL","http://storage_service:8002")


router = APIRouter()


def validate_admin(authorization: str | None): #מגיע מהפרונט  ובודק האם מבצע הפעולה זה אדמין 

    if not authorization: #כלומר משתמש לא מחובר 
        raise HTTPException(status_code=401,detail="Missing Authorization header"
        )

    try:
        response = requests.get(        #שולח את ההרשאות לבדיקה לסרוויס אחר ובודק תוקן 
            f"{AUTH_SERVICE_URL}/validate-admin",
            headers={
                "Authorization": authorization
            },
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Auth service is unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=403,
            detail="Only admin can perform this action"
        )

#שולח תמונה ל storge סוויס כדי להעלות תמונה
def upload_image_to_storage(product_id: str,image: UploadFile) -> str:

    try:
        response = requests.post(
            f"{STORAGE_SERVICE_URL}/images/products/{product_id}",
            files={
                "image": (
                    image.filename,
                    image.file,
                    image.content_type
                )
            },
            timeout=30  #אם הסרויס לא מצליח תוך 30 שניות הבקשה נכשלת
        )

    except requests.RequestException:
        raise HTTPException(status_code=503,detail="Storage service is unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500,detail=f"Image upload failed: {response.text}"
        )

    return response.json()["image_url"]


@router.post("/products")
def create_product(name: str = Form(...),description: str = Form(...),price: float = Form(...),category: str = Form(...),
    stock_count: int = Form(...),
    image: UploadFile | None = File(None),
    authorization: str | None = Header(None)
):

    validate_admin(authorization)

    if price <= 0:
        raise HTTPException(status_code=400,
            detail="Price must be positive"
        )

    if stock_count < 0:
        raise HTTPException(status_code=400,
            detail="Stock count cannot be negative"
        )

    product_id = str(uuid4())#מזהה יחודי למוצר

    image_url = None#כי אולי אין תמונה

    if image is not None and image.filename:#בודק אם נשלחה תמונה ואם יש לה שם
        image_url = upload_image_to_storage(#מעלה תמונה ומחזיר url של תמונה
            product_id=product_id,
            image=image
        )

    product = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "stock_count": stock_count,
        "image_url": image_url
    }

    es.index(
        index=PRODUCTS_INDEX,
        id=product_id,
        document=product,
        refresh=True#תעדכן מייד את האינדקס
    )

    return {
        "id": product_id,
        **product  #פותח את כל המילון במקום שיהיה מילון מקונן
    }


@router.get("/products")
def get_products(
    skip: int = Query(0, ge=0),#לא עובד טוב
    limit: int = Query(100, ge=1, le=200)
):

    result = es.search(
        index=PRODUCTS_INDEX,
        query={
            "match_all": {}
        },
        from_=skip,
        size=limit
    )

    products = []

    for hit in result["hits"]["hits"]:
        products.append(
            {
                "id": hit["_id"],
                **hit["_source"]
            }
        )

    return products


@router.get("/products/{product_id}")
def get_product_by_id(product_id: str):

    try:
        result = es.get(
            index=PRODUCTS_INDEX,
            id=product_id
        )

        return {
            "id": result["_id"],
            **result["_source"]
        }

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="The product does not exist"
        )


@router.put("/products/{product_id}")
def update_product(product_id: str,product: dict,authorization: str | None = Header(None)
):

    validate_admin(authorization)

    allowed_fields = { #איזה שדות מותר לעדכן 
    "name",
    "description",
    "price",
    "category",
    "stock_count",
    "image_url"
}

    update_data = {}

    for key, value in product.items():
        if key in allowed_fields and value is not None:#בודק אם השדה מותר לשנות ויש נתון שם
            update_data[key] = value

    if not update_data:#אם אין שדות חוקיים
        raise HTTPException(status_code=400,detail="No valid fields to update"
        )

    if "price" in update_data and float(update_data["price"]) <= 0:
        raise HTTPException(status_code=400,
            detail="Price must be positive"
        )

    if "stock_count" in update_data and int(update_data["stock_count"]) < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock count cannot be negative"
        )

    try:
        es.get(
            index=PRODUCTS_INDEX,
            id=product_id
        )

        es.update(
            index=PRODUCTS_INDEX,
            id=product_id,
            doc=update_data,
            refresh=True
        )

        updated_product = es.get(
            index=PRODUCTS_INDEX,
            id=product_id
        )

        return {
            "id": updated_product["_id"],
            **updated_product["_source"]
        }

    except NotFoundError:
        raise HTTPException(status_code=404,
            detail="The product does not exist"
        )


@router.post("/products/{product_id}/image")
def update_product_image(product_id: str,image: UploadFile = File(...),
    authorization: str | None = Header(None)#אומר לאפי לקחת את הערך מהHTTP HEADERS
):

    validate_admin(authorization)

    try:
        es.get(
            index=PRODUCTS_INDEX,
            id=product_id
        )

        image_url = upload_image_to_storage(
            product_id=product_id,
            image=image
        )

        es.update(
            index=PRODUCTS_INDEX,
            id=product_id,
            doc={
                "image_url": image_url
            },
            refresh=True
        )

        updated_product = es.get(
            index=PRODUCTS_INDEX,
            id=product_id
        )

        return {
            "id": updated_product["_id"],
            **updated_product["_source"]
        }

    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail="The product does not exist"
        )


@router.delete("/products/{product_id}")
def delete_product(
    product_id: str,
    authorization: str | None = Header(None)
):

    validate_admin(authorization)

    try:
        es.delete(
            index=PRODUCTS_INDEX,
            id=product_id,
            refresh=True
        )

        return {"message": "Product deleted good",
            "id": product_id
        }

    except NotFoundError:
        raise HTTPException(status_code=404,
            detail="The product does not exist"
        )