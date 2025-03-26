from sqlalchemy.orm import Session
from db.models import Dbbooking
from schemas import BookingCreate

def create_booking(db: Session, request: BookingCreate, user_id: int):
    new_booking = Dbbooking(
        user_id=user_id,
        hotel_id=request.hotel_id,
        check_in_date=request.check_in_date,
        check_out_date=request.check_out_date,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


def get_all_bookings(db: Session):
    return db.query(Dbbooking).all()

def get_booking(db: Session, booking_id: int):
    return db.query(Dbbooking).filter(Dbbooking.id == booking_id).first()

def delete_booking(db: Session, booking_id: int) -> bool:
    booking = db.query(Dbbooking).filter(Dbbooking.id == booking_id).first()
    if not booking:
        return False

    db.delete(booking)
    db.commit()
    return True

# db_booking.py

def get_bookings_for_user(db: Session, user_id: int):
    """Return all bookings for the given user_id."""
    return db.query(Dbbooking).filter(Dbbooking.user_id == user_id).all()
