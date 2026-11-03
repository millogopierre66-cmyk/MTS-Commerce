from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StockCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    description: str = Field(default="", max_length=255)


class StockIn(StockCreate):
    pass


class StockOut(StockCreate):
    pass


class StockAdjust(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=0)
    description: str = Field(
        default="Ajustement de stock",
        max_length=255,
    )


class StockResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    movement_type: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
