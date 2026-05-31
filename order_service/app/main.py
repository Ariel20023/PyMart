from fastapi import FastAPI

from app.routes.orders import router as orders_router
from app.database import Base, engine


Base.metadata.create_all(bind=engine)#יוצר טבלאות אם הם לא קיימות ב sqllite

app = FastAPI(title="Order Service")


@app.get("/health")
def health():
    return {"status": "good"}


app.include_router(orders_router)