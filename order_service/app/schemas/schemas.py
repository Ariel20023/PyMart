from datetime import datetime

from pydantic import BaseModel


class OrderItemResponse(BaseModel):#מוצר אחד
    product_id: str
    product_name: str
    quantity: int
    price: float


class OrderResponse(BaseModel):#הזמנה
    id: int
    user_email: str
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemResponse]