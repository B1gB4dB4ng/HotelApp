from decimal import Decimal
from typing import Optional, Literal
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
    name: str
    location: str
    is_activate:Literal["inactive", "active", "deleted"]="active"
    is_approved:bool=False
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
    #user_id: int  # Optional to return who owns it

    class Config:
        orm_mode = True