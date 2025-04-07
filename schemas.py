from decimal import Decimal
from datetime import date, timedelta
from operator import is_
import re
from typing import Annotated, Literal, Optional
from pydantic import (
    BaseModel,
    condecimal,
    EmailStr,
    StringConstraints,
    field_serializer,
    field_validator,
)
from enum import Enum


class IsActive(Enum):
    inactive = "inactive"
    active = "active"
    deleted = "deleted"


class UserBase(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    phone_number: Annotated[str, StringConstraints(min_length=10, max_length=15)]

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if not re.match(r"^\+?[0-9\s\-]+$", v):  # Basic phone format check
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
    is_superuser: Optional[bool] = None  # Remove default=False
    current_password: Optional[str] = None

    @field_validator("current_password")
    def validate_current_password_when_needed(cls, v, info):
        """Validate current_password only when sensitive fields are being changed"""
        data = info.data
        sensitive_fields = ["username", "email", "password"]

        if any(field in data and data[field] is not None for field in sensitive_fields):
            if not v:
                raise ValueError(
                    "Current password required for security-sensitive changes"
                )
        return v


class UpdateUserResponse(BaseModel):
    message: str
    user: UserDisplay
    access_token: Optional[str] = None
    token_type: Optional[str] = None


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
    is_active: Literal["inactive", "active", "deleted"] = "active"
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

    @field_validator("room_id")
    def validate_room_id(cls, v):
        if v == 0:
            raise ValueError("room_id cannot be 0")
        return v

    @field_validator("hotel_id")
    def validate_hotel_id(cls, v):
        if v == 0:
            raise ValueError("hotel_id cannot be 0")
        return v


class BookingCreate(BookingBase):
    user_id: int  # The user making the booking


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class BookingShow(BookingBase):
    id: int
    user_id: int
    total_cost: Optional[float]
    cancel_reason: Optional[str] = None
    is_active: str  # Change from IsActive enum to string
    status: BookingStatus = BookingStatus.pending

    class Config:
        from_attributes = True
        json_encoders = {
            Enum: lambda v: v.value  # This ensures enums are serialized as strings
        }


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


# -----------------------------------------------------------
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


# ---------------------------------------------------------------------


# -----------------------------------------------------------


class HotelSearch(BaseModel):
    search_term: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    location: Optional[str] = None
