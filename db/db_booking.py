from sqlalchemy.orm import Session
from db.models import Dbbooking, Dbhotel
from schemas import BookingCreate
from fastapi import HTTPException

# create a booking
def create_booking(db: Session, request: BookingCreate, user_id: int):
    # Check if the hotel actually exists
    hotel = db.query(Dbhotel).filter(Dbhotel.id == request.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel does not exist.")
    
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

# getting all the bookings
def get_all_bookings(db: Session):
    return db.query(Dbbooking).all()

# Return the bookings for the given booking_id
def get_booking(db: Session, booking_id: int):
    # Find the booking
    booking = db.query(Dbbooking).filter(Dbbooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Check existence of the hotel
    hotel = db.query(Dbhotel).filter(Dbhotel.id == booking.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel does not exist for this booking.")

    # both booking and hotel exist
    return booking


def delete_booking(db: Session, booking_id: int) -> bool:
    booking = db.query(Dbbooking).filter(Dbbooking.id == booking_id).first()
    if not booking:
        return False

    db.delete(booking)
    db.commit()
    return True


# Return all bookings for the given user_id
def get_bookings_for_user(db: Session, user_id: int):
    return db.query(Dbbooking).filter(Dbbooking.user_id == user_id).all()

