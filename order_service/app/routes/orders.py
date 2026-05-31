from fastapi import APIRouter, Header, HTTPException

from app.database import SessionLocal
from app.models.models import Order, OrderItem
from app.schemas.schemas import OrderResponse
from app.services.inventory_client import reserve_inventory
from app.services.auth_client import get_current_user
from app.services.cart_client import get_cart, clear_cart
from app.services.rabbitmq_publisher import publish_order_placed_event


router = APIRouter()


@router.post("/orders", response_model=OrderResponse)#יוצר הזמה חדשה מיתוך עגלה
def create_order(authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    cart = get_cart(authorization)#מביא את העגלה

    if not cart["items"]:
        raise HTTPException(status_code=400,#בקשה לא הגיונית
            detail="Cart is empty"
        )
    reserve_inventory(#בודק שיש מלאי
    cart["items"],
    authorization
                )

    db = SessionLocal()

    order = Order(#יצירת הזמנה 
        user_email=user["email"],
        status="pending",
        total_price=cart["total_price"]
    )

    db.add(order)
    db.flush()#שולח ל db ומקבל id 

    for item in cart["items"]:#יצירת מוצרים שבתוך ההזמנה
        order_item = OrderItem(
            order_id=order.id,#מחבר את ההזמנה למוצר
            product_id=item["product_id"],
            product_name=item["name"],
            quantity=item["quantity"],
            price=item["price"]
        )

        db.add(order_item)

    db.commit()
    db.refresh(order)#עושה עדכון סופי של id ןנוצר ב  ומחבר את המוצרים עצמם

    order_data = {#בונים הזמנה כדי לשלוח לrabbitmq וזה מילון מסודר ולא אובייקט של sql
        "order_id": order.id,
        "user_email": order.user_email,
        "status": order.status,
        "total_price": order.total_price,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in order.items
        ]
    }

    publish_order_placed_event(order_data)#שולח לראביט

    clear_cart(authorization)#אחרי שההזמנה הצליחה מוחקים את העגלה של המשתמש מהcart service 

    db.close()#נסגר חיבור לsqllite 

    return order#מחזיר לפרונט את ההזמנה שבוצעה


@router.get("/orders", response_model=list[OrderResponse])#מחזיר למשתמש את כל ההזמנות שלו
def list_orders(authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    db = SessionLocal()#חיבור ל sql

    orders = (
        db.query(Order).filter(Order.user_email == user["email"]).order_by(Order.created_at.desc()).all())#ממין לפי תאריך

    db.close()

    return orders#מחזיר רשימת הזמנות

#patch  זה כימעדכנים חלק קטן מהorder
@router.patch("/orders/{order_id}/status", response_model=OrderResponse)#מעדכן סטטוס הזמנה
def update_order_status(order_id: int,status: str,authorization: str | None = Header(None)):
    user = get_current_user(authorization)

    if user["role"] != "admin":#רק לאדמין מותר לעדכון סטטוס
        raise HTTPException(
            status_code=403,
            detail="Only admin can update order status"
        )

    allowed_statuses = [#רשינת סטטוסים חוקיים 
        "pending",
        "confirmed",
        "shipped",
        "delivered"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    db = SessionLocal()

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        db.close()
        raise HTTPException(status_code=404,detail="Order not found")

    order.status = status

    db.commit()#שומר בזיכרון 
    db.refresh(order)#טוען מחדש את האוסבייקט אחרי השינוי
    db.close()#ואז סוגר

    return order