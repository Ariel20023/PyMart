from fastapi import FastAPI

from app.routes.users import router
from app.database.database import Base, engine
from app.seed.seed_admin import seed_admin

Base.metadata.create_all(bind=engine)

seed_admin()

app = FastAPI(title="Auth Service")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "very good"}