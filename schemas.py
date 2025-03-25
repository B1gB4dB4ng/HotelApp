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
        from_attributes = True


class HotelBase(BaseModel):
    name: str
    location: str
    description: Optional[str]
    price: Decimal
    img_link: Optional[str]


class HotelDisplay(BaseModel):
    id: int
    name: str
    location: str
    description: Optional[str]
    price: Decimal
    img_link: Optional[str]
    is_approved: bool
    # user_id: int  # Optional to return who owns it

    class Config:
        from_attributes = True

#######
class HotelSearch(BaseModel):
    search_term: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    location: Optional[str] = None