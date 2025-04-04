from decimal import Decimal
from datetime import date, timedelta
import re
from typing import Annotated, Literal, Optional, List
from pydantic import condecimal

from pydantic import (
    BaseModel,
    EmailStr,
    StringConstraints,
    Field,
    field_validator,
    field_serializer,
)
from enum import Enum

# User

class UserBase(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    phone_number: Annotated[str, StringConstraints(min_length=10, max_length=15)]

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if not re.match(r"^\+?[0-9\s\-]+$", v):
            raise ValueError("Invalid phone number format")
        return v


class UserDisplay(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    phone_number: Annotated[str, StringConstraints(min_length=10, max_length=15)]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    is_superuser: Optional[bool] = None
    current_password: Optional[str] = None

    @field_validator("current_password")
    def validate_current_password_when_needed(cls, v, info):
        data = info.data
        sensitive_fields = ["username", "email", "password"]
        if any(field in data and data[field] is not None for field in sensitive_fields):
            if not v:
                raise ValueError("Current password required for security-sensitive changes")
        return v


class UpdateUserResponse(BaseModel):
    message: str
    user: UserDisplay
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Hotel

class HotelBase(BaseModel):
    name: str
    location: str
    is_active: Literal["inactive", "active", "deleted"] = "active"
    description: Optional[str]
    img_link: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    is_approved: bool = False


class HotelDisplay(BaseModel):
    id: int
    name: str
    location: str
    description: Optional[str]
    img_link: Optional[str]
    is_approved: bool
    avg_review_score: Optional[Decimal]
    phone_number: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


class UpdateHotelResponse(BaseModel):
    message: str
    hotel: HotelDisplay

# Room

class RoomBase(BaseModel):
    room_number: str
    description: Optional[str] = None
    price_per_night: Decimal
    wifi: bool = False
    air_conditioner: bool = False
    tv: bool = False
    status: Literal["available", "booked"] = "available"
    bed_count: int


class RoomCreate(RoomBase):
    hotel_id: int
    is_active: Literal["inactive", "active", "deleted"] = Field(
        default="active",
        description="Room status: 'active', 'inactive', or 'deleted'",
        example="active"
    )


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


class RoomUpdate(BaseModel):
    description: Optional[str] = None
    price_per_night: Optional[Decimal] = None
    wifi: Optional[bool] = None
    air_conditioner: Optional[bool] = None
    tv: Optional[bool] = None
    status: Optional[Literal["available", "booked", "unavailable"]] = None
    bed_count: Optional[int] = None
    is_active: Optional[Literal["inactive", "active", "deleted"]] = "active"


class RoomSearch(BaseModel):
    search_term: Optional[str] = None
    amenities: Optional[List[str]] = Field(None, example=["wifi", "air_conditioner"])
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    check_in: date
    check_out: date
    location: Optional[str] = None

# Booking

class BookingBase(BaseModel):
    hotel_id: int
    room_id: int
    check_in_date: date = date.today()
    check_out_date: date = date.today() + timedelta(days=1)


class BookingCreate(BookingBase):
    pass


class BookingShow(BookingBase):
    id: int
    user_id: int
    total_cost: Optional[float]
    cancel_reason: Optional[str] = None
    status: Literal["pending", "confirmed", "cancelled"] = "pending"

    class Config:
        from_attributes = True


class BookingUpdate(BookingBase):
    status: Optional[Literal["pending", "confirmed", "cancelled"]] = "pending"
    cancel_reason: Optional[str] = None

# Payment

class PaymentBase(BaseModel):
    booking_id: int
    amount: Decimal
    status: Literal["pending", "completed", "failed", "refunded"]
    payment_date: date


class PaymentShow(PaymentBase):
    id: int

    class Config:
        from_attributes = True

# Review


#-----------------------------------------------------------
class IsReviewStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"

class ReviewBase(BaseModel):
    user_id: int
    hotel_id: int
    booking_id: int
    rating: condecimal(max_digits=2, decimal_places=1, ge=1.0, le=5.0)
    comment: Optional[str]
    created_at: date
    status: IsReviewStatus = IsReviewStatus.pending

class ReviewShow(ReviewBase):
    id: int

    class Config:
        from_attributes = True


# models.py or schemas.py
class ReviewUpdate(BaseModel):
    rating: Optional[condecimal(gt=0, le=5, max_digits=2, decimal_places=1)] = None
    comment: Optional[str] = None


class HotelSearch(BaseModel):
    search_term: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    location: Optional[str] = None
