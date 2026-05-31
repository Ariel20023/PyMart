from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    item_total: float
    image_url: str |None = None
    stock_count: int


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: float