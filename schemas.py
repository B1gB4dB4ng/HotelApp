from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class UserDisplay(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True


class HotelBase(BaseModel):
    title: str
    description: Optional[str] = None
    img_link: Optional[str] = None
    price: Decimal
    location: str
    is_active: bool = True
    owner_username: str


class HotelDisplay(HotelBase):
    id: int
    title: str
    description: Optional[str] = None
    img_link: Optional[str] = None
    price: Decimal
    location: str
    is_active: bool
    owner_username: str

    class Config:
        orm_mode = True
