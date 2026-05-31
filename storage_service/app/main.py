from fastapi import FastAPI

from app.routes.images import router

app = FastAPI(title="Storage Service")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "good"}