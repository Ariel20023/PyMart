from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String
from app.database.database import Base


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    shipping_address: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    shipping_address = Column(String)
    role = Column(String, default="user")
