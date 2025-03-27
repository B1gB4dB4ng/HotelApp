from decimal import Decimal
from datetime import date
from typing import Literal, Optional
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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class HotelBase(BaseModel):
    name: str
    location: str
    is_active: Literal["inactive", "active", "deleted"] = "active"
    is_approved: bool = False
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


class BookingBase(BaseModel):
    hotel_id: int
    check_in_date: date
    check_out_date: date


class BookingCreate(BookingBase):
    pass


class BookingShow(BookingBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    hotel_id: Optional[int] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    # 'is_active' should not be included here or can be restricted
    # 'user_id' should not be included as it shouldn't be updated

    class Config:
        from_attributes = True
