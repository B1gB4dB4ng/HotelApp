from decimal import Decimal
from datetime import date, timedelta
from typing import Literal, Optional
from pydantic import BaseModel,  condecimal, field_serializer
from enum import Enum


class UserBase(BaseModel):
    username: str
    email: str
    password: str
    phone_number: Optional[str]  # Added phone_number


class UserDisplay(BaseModel):
    username: str
    email: str
    phone_number: Optional[str]  # Added phone_number

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class HotelBase(BaseModel):
    name: str
    location: str
    is_active: Literal["inactive", "active", "deleted"] = "active"
    description: Optional[str]
    img_link: Optional[str]
    phone_number: Optional[str]  # Added phone_number
    email: Optional[str]  # Added email
    is_approved: bool = False


class HotelDisplay(BaseModel):
    id: int
    name: str
    location: str
    description: Optional[str]
    img_link: Optional[str]
    is_approved: bool
    avg_review_score: Optional[Decimal]  # Added avg_review_score
    phone_number: Optional[str]  # Added phone_number
    email: Optional[str]  # Added email

    class Config:
        from_attributes = True


class UpdateHotelResponse(BaseModel):
    message: str
    hotel: HotelDisplay


class RoomBase(BaseModel):
    room_number: str
    description: Optional[str]
    price_per_night: Decimal
    #is_active: Literal["inactive", "active", "deleted"]
    wifi: bool = False
    air_conditioner: bool = False
    tv: bool = False
    status: Literal["available", "booked"] = "available"
    bed_count: int


class RoomDisplay(BaseModel):
    id: int
    hotel_id: int
    room_number: str
    description: Optional[str]
    price_per_night: Decimal
    is_active: str
    wifi: bool
    air_conditioner: bool
    tv: bool
    status: str
    bed_count: int

    class Config:
        from_attributes = True

    @field_serializer("is_active", "status")  # ✅ Convert Enum to string
    def serialize_enum(value: Enum) -> str:
        return value.value if isinstance(value, Enum) else value


class BookingBase(BaseModel):
    hotel_id: int  # The hotel this booking is associated with
    room_id: int  # Room booked by the guest
    check_in_date: date = date.today()
    check_out_date: date = date.today() + timedelta(days=1)


class BookingCreate(BookingBase):
    pass


class BookingShow(BookingBase):
    id: int
    user_id: int
    total_cost: Optional[float]  # This will be calculated and returned to the user
    cancel_reason: Optional[str] = None  # Can be included if the booking is canceled

    # Set the default value for status to "pending" in the response
    status: Literal["pending", "confirmed", "cancelled"] = "pending"

    class Config:
        from_attributes = True


class BookingUpdate(BookingBase):
    status: Optional[Literal["pending", "confirmed", "cancelled"]] = (
        "pending"  # Default to "pending"
    )
    cancel_reason: Optional[str] = None  # Optional reason, can be filled when canceling


class PaymentBase(BaseModel):
    booking_id: int
    amount: Decimal
    status: Literal["pending", "completed", "failed", "refunded"]
    payment_date: date


class PaymentShow(PaymentBase):
    id: int

    class Config:
        from_attributes = True

#----------------------||Review's schemas||----------------------
class ReviewBase(BaseModel):
    user_id: int
    hotel_id: int
    booking_id: int
    rating: condecimal(max_digits=2, decimal_places=1, ge=1.0, le=5.0)
    comment: Optional[str]
    created_at: date
    status: Literal["pending", "approved", "rejected"] = "pending"


class ReviewShow(ReviewBase):
    id: int

    class Config:
        from_attributes = True


# models.py or schemas.py
class ReviewUpdate(BaseModel):
    rating: Optional[condecimal(gt=0, le=5, max_digits=2, decimal_places=1)] = None
    comment: Optional[str] = None

#---------------------------------------------------------------------




class HotelSearch(BaseModel):
    search_term: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    location: Optional[str] = None
