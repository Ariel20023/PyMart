from datetime import datetime
from sqlalchemy import Column,Integer,String,Float,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):#ההזמנה עצמה
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_email = Column(String)
    status = Column(String, default="pending")
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)#אם לא שלחו ערך תשתמש בנוכחי
    items = relationship("OrderItem",back_populates="order",cascade="all, delete-orphan")#מחבר בין הזמנה למוצרים שהזמנה אחת יש בה הרבה מוצרים ואם מוחקים הזמנה כל המוצרים נמחקים יחד


class OrderItem(Base):#המוצרים שלה
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer,ForeignKey("orders.id"))
    product_id = Column(String)
    product_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    order = relationship("Order",back_populates="items")#מקשר לטבלה של order