from pydantic import BaseModel, Field


class InventoryItem(BaseModel):#מוצר אחד לבדיקה או לשריון
    product_id: str
    quantity: int = Field(gt=0)


class ReserveInventoryRequest(BaseModel):#בקשה שהorder service ישלח של מוצרים
    items: list[InventoryItem]


class UpdateStockRequest(BaseModel):#נותן לאדמין לעדכן ידנית
    stock_count: int = Field(ge=0)