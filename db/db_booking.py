from sqlalchemy.orm import Session
from db.models import Dbbooking, Dbuser, IsActive
from schemas import BookingCreate, BookingUpdate


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


def get_booking_by_id(db: Session, booking_id: int):
    return (
        db.query(Dbbooking)
        .filter(
            Dbbooking.id == booking_id,
            Dbbooking.is_active == IsActive.active,  # Exclude soft-deleted bookings
        )
        .first()
    )


def soft_delete_booking(db: Session, booking_id: int):
    booking = db.query(Dbbooking).filter(Dbbooking.id == booking_id).first()

    if not booking:
        return None  # Return None if no booking is found

    booking.is_active = (
        IsActive.deleted
    )  # Mark the booking as inactive instead of deleting
    db.commit()
    db.refresh(booking)
    return booking  # Return the updated booking


def get_all_bookings_for_admin(db: Session):
    """Fetch all active bookings (only for super admins)"""
    return db.query(Dbbooking).filter(Dbbooking.is_active == IsActive.active).all()


def get_bookings_for_user(db: Session, user: Dbuser):
    return (
        db.query(Dbbooking)
        .filter(Dbbooking.user_id == user.id, Dbbooking.is_active == "active")
        .all()
    )


def update_booking_in_db(
    db: Session, booking_id: int, request: BookingUpdate
) -> Dbbooking:
    # Query the booking by ID
    booking = db.query(Dbbooking).filter(Dbbooking.id == booking_id)

    # Check if the booking exists
    if not booking.first():
        return None  # Return None if the booking is not found

    # Prepare data for updating the booking
    request_data = request.dict(exclude_unset=True)

    # Update the booking fields (only the fields that are included in the request)
    booking.update(request_data)

    # Commit the changes to the database
    db.commit()

    # Return the updated booking (optional - if you want to fetch it back from DB)
    updated_booking = booking.first()
    return updated_booking
