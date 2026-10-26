from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(from_attributes=True)


class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int | None
    user_id: int
    total: float
    status: str
    cancelled_at: datetime | None = None
    cancelled_by: int | None = None
    created_at: datetime
    items: list[SaleItemResponse]

    model_config = ConfigDict(from_attributes=True)
