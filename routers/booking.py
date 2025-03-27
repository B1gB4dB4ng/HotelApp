from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth.oauth2 import get_current_user
from db.database import get_db
from db import db_booking
from db.models import Dbbooking, Dbhotel, Dbuser
from schemas import BookingCreate, BookingShow, BookingUpdate

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("/", response_model=BookingShow)
def create_a_booking(
    request: BookingCreate,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    # Check if check_in_date is before check_out_date
    if request.check_in_date >= request.check_out_date:
        raise HTTPException(
            status_code=400, detail="check_in_date must be before check_out_date."
        )

    # Check if the hotel exists
    hotel = db.query(Dbhotel).filter(Dbhotel.id == request.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found.")

    # Create the booking if the hotel exists
    new_booking = db_booking.create_booking(db, request, user_id=user.id)
    return new_booking


# FOR SUPERADMIN
@router.get("/", response_model=List[BookingShow])
def get_all_bookings_for_admin(
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    if not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to view all bookings"
        )

    return db_booking.get_all_bookings_for_admin(db)


@router.get("/user/{user_id}", response_model=List[BookingShow])
def get_user_bookings(
    user_id: int,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    if not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to view other users' bookings"
        )

    bookings = db_booking.get_bookings_for_user(db, user_id)
    return bookings


# FOR USER
@router.get("/{booking_id}", response_model=BookingShow)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),  # Get the current logged-in user
):
    booking = db_booking.get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Only allow access if the user owns the booking or is a super admin
    if not user.is_superuser and booking.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this booking"
        )

    return booking


@router.get("/mybookings/", response_model=List[BookingShow])
def get_bookings_for_user(
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    bookings = db_booking.get_bookings_for_user(db, user)  # Pass the full user object
    return bookings


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    booking = db_booking.soft_delete_booking(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=404, detail=f"Booking with ID {booking_id} not found"
        )

    if not user.is_superuser and booking.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail=f"Not authorized to delete booking with ID {booking_id}",
        )

    return {"message": f"Booking with ID {booking_id}  deleted successfully"}


@router.patch("/{booking_id}", response_model=BookingShow)
def update_booking(
    booking_id: int,
    request: BookingUpdate,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    # Fetch the booking using the function from db_booking
    booking = db.query(Dbbooking).filter(Dbbooking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Authorization: Only allow the user to update their own booking or if they are an admin
    if not user.is_superuser and booking.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this booking"
        )

    if "user_id" in request.dict(exclude_unset=True) and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update the 'user_id' field"
        )

    # Authorization for 'is_active': Only admins can update the 'is_active' field
    if "is_active" in request.dict(exclude_unset=True) and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update the 'is_active' field"
        )

    # Now that we've validated the authorization, call the function to update the booking
    updated_booking = db_booking.update_booking_in_db(db, booking_id, request)

    if not updated_booking:
        raise HTTPException(
            status_code=404, detail="Booking not found or could not be updated"
        )

    return updated_booking
