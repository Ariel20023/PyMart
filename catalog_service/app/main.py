from fastapi import FastAPI

from app.routes.products import router as products_router
from app.services.elastic import (
    wait_for_elasticsearch,
    create_products_index,
    seed_products
)

app = FastAPI(title="Catalog Service")


@app.on_event("startup")
def startup():
    wait_for_elasticsearch()
    create_products_index()
    seed_products()


@app.get("/health")
def health():
    return {"status": "good"}


app.include_router(products_router)