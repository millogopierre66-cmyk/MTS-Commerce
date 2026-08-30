from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class StockCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0)
    description: str = ""


class StockIn(StockCreate):
    pass


class StockOut(StockCreate):
    pass

class StockAdjust(BaseModel):
    product_id: int
    quantity: float = Field(ge=0)
    description: str = "Ajustement de stock"

class StockResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    movement_type: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

