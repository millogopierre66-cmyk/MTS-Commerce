from datetime import datetime

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaleCreate(BaseModel):
    customer_id: int | None = None
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int | None
    total: float
    created_at: datetime
    items: list[SaleItemResponse]

    class Config:
        from_attributes = True