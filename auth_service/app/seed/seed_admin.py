import os
from passlib.context import CryptContext
from app.database.database import SessionLocal
from app.schemas.schemas import User

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@pymart.com")
ADMIN_SHIPPING_ADDRESS = os.getenv("ADMIN_SHIPPING_ADDRESS", "8200")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_admin():
    db = SessionLocal()

    existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if existing_admin:
        db.close()
        return

    password_hash = pwd_context.hash(ADMIN_PASSWORD)

    admin = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password_hash=password_hash,
        shipping_address=ADMIN_SHIPPING_ADDRESS,
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()
