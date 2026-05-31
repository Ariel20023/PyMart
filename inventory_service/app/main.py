from fastapi import FastAPI

from app.routes.inventory import router as inventory_router


app = FastAPI(title="Inventory Service")


@app.get("/health")
def health():
    return {"status": "good"}


app.include_router(inventory_router)