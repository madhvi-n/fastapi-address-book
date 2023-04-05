from pydantic import BaseModel
from typing import Optional


class AddressBase(BaseModel):
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str
    latitude: float
    longitude: float


class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int

    class Config:
        orm_mode = True
