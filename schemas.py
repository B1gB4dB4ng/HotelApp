from decimal import Decimal
from datetime import date, timedelta
import re
from typing import Annotated, Literal, Optional
from pydantic import (
    BaseModel,
    EmailStr,
    StringConstraints,
    field_serializer,
    field_validator,
)
from enum import Enum


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


class ReviewBase(BaseModel):
    user_id: int
    hotel_id: int
    booking_id: int
    rating: Decimal
    comment: Optional[str]
    created_at: date


class ReviewShow(ReviewBase):
    id: int

    class Config:
        from_attributes = True


class HotelSearch(BaseModel):
    search_term: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    location: Optional[str] = None
