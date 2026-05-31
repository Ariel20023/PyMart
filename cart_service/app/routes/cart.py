import json

from fastapi import APIRouter, Header, HTTPException
from app.schemas.schemas import (CartItemCreate,CartItemUpdate,CartResponse)
from app.services.redis_client import redis_client
from app.services.auth_client import get_current_user
from app.services.catalog_client import get_product


router = APIRouter()

CART_TTL_SECONDS = 60 * 60 * 24   


def get_cart_key(user_email: str):#key for redis
    return f"cart:{user_email}"


def load_cart(cart_key: str): #טוען עגלה מ redis
    cart_data = redis_client.get(cart_key)

    if not cart_data:  #כדי שלא יקרוס אם צ
        return {
            "items": {}
        }

    return json.loads(cart_data)


def save_cart(cart_key: str, cart: dict): #save in radis
    redis_client.set(
        cart_key,
        json.dumps(cart),
        ex=CART_TTL_SECONDS  #אחרי הזמן הזה זה ימחק
    )


def build_cart_response(cart: dict):#לוקח עגלה ומוציא תשובה מסודרת
    items = []
    total_price = 0

    for product_id, quantity in cart["items"].items():
        product = get_product(product_id)#מביא את המוצר לפי ה id מהקטלוג

        item_total = product["price"] * quantity#מחשב מחיר 
        total_price += item_total

        items.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],#מחיר ליחידה
            "quantity": quantity,
            "item_total": item_total,#מחיר כולל 
            "image_url": product.get("image_url"),#תמונה של מוצר
            "stock_count": product["stock_count"]#כמה יחידות יש במלאי
        })

    return {
        "items": items,
        "total_price": total_price
    }


@router.get("/cart", response_model=CartResponse)
def get_cart(authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    cart_key = get_cart_key(user["email"])
    cart = load_cart(cart_key)

    if cart["items"]:#שומר את המוצר 
        save_cart(cart_key, cart)#כדי שזה יתחיל לספור את 24 שעות רק אחרי סיום התהליך וההתעסקות

    return build_cart_response(cart)


@router.post("/cart/items", response_model=CartResponse)
def add_item_to_cart(item: CartItemCreate,authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    product = get_product(item.product_id)#בודק אם יש מוצר כזה כבר 

    if product["stock_count"] <= 0:
        raise HTTPException(status_code=400,detail="Product is out of stock"
        )

    if item.quantity > product["stock_count"]:#בודק אם ביקש יותר מהמלאי הקיים
        raise HTTPException(status_code=400,detail="Requested quantity is greater than available stock"
        )

    cart_key = get_cart_key(user["email"])#יוצר מפתח לעגלה
    cart = load_cart(cart_key)#טוען את העגלה

    current_quantity = cart["items"].get(item.product_id, 0)#בודק אם יש כבר את המוצר הזה בעגלה (דיפולטיבי 0)
    new_quantity = current_quantity + item.quantity

    if new_quantity > product["stock_count"]:#בודק אם בעגלה יש יותר מהמלאי
        raise HTTPException(status_code=400,
            detail="Cart quantity is greater than available stock"
        )

    cart["items"][item.product_id] = new_quantity

    save_cart(cart_key, cart)

    return build_cart_response(cart)

#מעדכן כמות של מוצר שכבר נמצא
@router.put("/cart/items/{product_id}", response_model=CartResponse)
def update_cart_item(product_id: str,item: CartItemUpdate,
    authorization: str | None = Header(None)
):
    user = get_current_user(authorization)

    product = get_product(product_id)#מביא את פרטי המוצר

    if product["stock_count"] <= 0:#בודק אם נשאר במלאי
        raise HTTPException(status_code=400,detail="Product is out of stock"
        )

    if item.quantity > product["stock_count"]:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity is greater than available stock"
        )

    cart_key = get_cart_key(user["email"])
    cart = load_cart(cart_key)

    if product_id not in cart["items"]:
        raise HTTPException(
            status_code=404,
            detail="Product is not in cart"
        )

    cart["items"][product_id] = item.quantity#עדכון הכמות

    save_cart(cart_key, cart)

    return build_cart_response(cart)


@router.delete("/cart/items/{product_id}", response_model=CartResponse)
def remove_cart_item(
    product_id: str,
    authorization: str | None = Header(None)
):
    user = get_current_user(authorization)

    cart_key = get_cart_key(user["email"])
    cart = load_cart(cart_key)

    if product_id not in cart["items"]:
        raise HTTPException(
            status_code=404,
            detail="Product is not in cart"
        )

    del cart["items"][product_id]

    save_cart(cart_key, cart)

    return build_cart_response(cart)


@router.delete("/cart")
def clear_cart(authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    cart_key = get_cart_key(user["email"])
    redis_client.delete(cart_key)

    return {
        "message": "Cart cleared successfully"
    }