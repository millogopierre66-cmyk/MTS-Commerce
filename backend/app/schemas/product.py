from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    reference: str
    barcode: str
    name: str
    description: str = ""
    category: str

    purchase_price: float = Field(ge=0)
    selling_price: float = Field(ge=0)

    quantity: int = Field(default=0, ge=0)

    alert_stock: int = Field(default=5, ge=0)

    minimum_stock: float = Field(default=5, ge=0)

    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    reference: str | None = None
    barcode: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None

    purchase_price: float | None = Field(
        default=None,
        ge=0
    )

    selling_price: float | None = Field(
        default=None,
        ge=0
    )

    alert_stock: int | None = Field(
        default=None,
        ge=0
    )

    minimum_stock: float | None = Field(
        default=None,
        ge=0
    )

    active: bool | None = None

    model_config = ConfigDict(
        extra="forbid"
    )


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )