from sqlalchemy.orm import Session
from db.models import Dbbooking
from schemas import BookingCreate

def create_booking(db: Session, request: BookingCreate, user_id: int):
    """
    Create a new booking for the given user with the provided booking data.
    """
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