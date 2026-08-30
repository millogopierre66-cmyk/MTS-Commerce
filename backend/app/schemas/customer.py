from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr | None = None
    address: str = ""
    city: str = ""


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    city: str | None = None
    active: bool | None = None


class CustomerResponse(CustomerBase):
    id: int
    active: bool

    model_config = ConfigDict(from_attributes=True)