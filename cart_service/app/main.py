from fastapi import FastAPI
from app.routes.cart import router as cart_router

app = FastAPI(title="Cart Service")


@app.get("/health")
def health():
    return {"status": "good"}


app.include_router(cart_router)