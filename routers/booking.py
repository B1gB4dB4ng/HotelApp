from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db import db_booking
from schemas import BookingCreate, BookingShow

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("/", response_model=BookingShow)
def create_a_booking(
    request: BookingCreate,
    db: Session = Depends(get_db)
):
    # For now, we can hardcode or accept user_id as a parameter.
    # Let's just assume user_id is 1 for demonstration purposes.
    user_id = 1

    if request.check_in_date >= request.check_out_date:
        raise HTTPException(
            status_code=400, detail="check_in_date must be before check_out_date."
        )

    new_booking = db_booking.create_booking(db, request, user_id)
    return new_booking

@router.get("/", response_model=List[BookingShow])
def get_all_bookings(db: Session = Depends(get_db)):
    """
    Get all bookings in the system.
    """
    bookings = db_booking.get_all_bookings(db)
    return bookings


@router.get("/{booking_id}", response_model=BookingShow)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db_booking.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.get("/user/{user_id}", response_model=List[BookingShow])
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db_booking.get_bookings_for_user(db, user_id)
    return bookings


@router.delete("/{booking_id}")
def delete_a_booking(booking_id: int, db: Session = Depends(get_db)):
    success = db_booking.delete_booking(db, booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"detail": "Booking deleted successfully"}





