import os
from sqlalchemy import create_engine #יוצר חיבור למסד נתונים
from sqlalchemy.orm import sessionmaker, declarative_base #יוצר בסיס לכל המחסני נתונים ויוצר sessions

SQLITE_PATH = os.getenv("SQLITE_PATH", "/tmp/users.db")

engine = create_engine(f"sqlite:///{SQLITE_PATH}",connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine) #פותח חיבור למסד
Base = declarative_base()#מחלקת בסיס לכל התבלאות