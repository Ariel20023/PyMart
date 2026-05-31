import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


SQLITE_PATH = os.getenv("SQLITE_PATH","/tmp/orders.db")

engine = create_engine(f"sqlite:///{SQLITE_PATH}")#חיבור למסד עצמו

SessionLocal = sessionmaker(bind=engine)#מאפשר לעבוד מול ה db

Base = declarative_base()#הבסיס של כל המודולים