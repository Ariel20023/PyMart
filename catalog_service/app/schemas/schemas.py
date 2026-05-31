from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    category: str
    stock_count: int = Field(ge=0)
    image_url: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = None
    stock_count: int | None = Field(default=None, ge=0)
    image_url: str | None = None


class ProductResponse(ProductCreate):
    id: str
