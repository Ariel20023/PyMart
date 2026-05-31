from fastapi import APIRouter, Header, HTTPException
from app.schemas.schemas import ReserveInventoryRequest,UpdateStockRequest
from app.services.auth_client import get_current_user
from app.services.catalog_client import get_product,update_product_stock



router = APIRouter()


@router.post("/inventory/reserve")#בודק שיש מספיק מלאי לפני יצירת הזמנה
def reserve_inventory(data: ReserveInventoryRequest,authorization: str |None = Header(None)):
    get_current_user(authorization)#בודק שהתוקן קיים ואם תקין

    for item in data.items:#עובר על כל מוצר בעגלה
        product = get_product(item.product_id)#מביא מוצר מהcatalog service 

        if product["stock_count"] < item.quantity:
            raise HTTPException(status_code=400,detail=f"Not enough stock for {product['name']}"
            )

    return {"message": "Stock reserved"}#הכול תקין


@router.post("/inventory/release")#מחזיר מלאי אם בקשה בוטלה או לדוגמא שתשלום נכשל
def release_inventory(data: ReserveInventoryRequest,authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    if user["role"] != "admin":#רק לאדמין מותר 
        raise HTTPException(status_code=403,detail="Only admin can release stock")

    for item in data.items:
        product = get_product(item.product_id)#מביא את המוצר מהקטלוג
        new_stock = (product["stock_count"] + item.quantity)
        update_product_stock(
            product_id=item.product_id,
            stock_count=new_stock,
            authorization=authorization
        )

    return {"message": "Stock released"}


@router.patch("/inventory/{product_id}/stock")# מאפשר לאדמין לעדכן ידנית את המחיר
def update_stock(product_id: str,data: UpdateStockRequest,authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    if user["role"] != "admin":
        raise HTTPException(status_code=403,
            detail="Only admin can update stock"
        )

    update_product_stock(
        product_id=product_id,
        stock_count=data.stock_count,
        authorization=authorization
    )

    return {"message": "Stock updated successfully"}