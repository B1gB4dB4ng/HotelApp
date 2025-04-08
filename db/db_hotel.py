from sqlalchemy.orm import Session
from db.models import Dbhotel, IsActive, Dbuser
from schemas import HotelBase
from sqlalchemy import or_
from typing import Optional
from fastapi import BackgroundTasks
from email_utils import send_email


def create_hotel(db: Session, request: HotelBase, owner_id: int):
    # Check if a hotel with the same name and location already exists
    existing_hotel = (
        db.query(Dbhotel)
        .filter(Dbhotel.name == request.name, Dbhotel.location == request.location)
        .first()
    )

    if existing_hotel:
        return None  # Return None if the hotel already exists

    # If no duplicate found, create a new hotel
    new_hotel = Dbhotel(
        name=request.name,
        location=request.location,
        description=request.description,
        img_link=request.img_link,
        phone_number=request.phone_number,
        email=request.email,
        owner_id=owner_id,
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel


# delete hotel
def delete_hotel(db: Session, id: int, background_tasks: BackgroundTasks):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()
    print(hotel)

    if hotel:
        hotel.is_active = IsActive.deleted  # Mark hotel as deleted
        db.commit()

        # Fetch the owner (Dbuser) to get the name
        owner = db.query(Dbuser).filter(Dbuser.id == hotel.owner_id).first()

# Add the background email sending task
        subject = "Hotel Deletion Notification"
        body = f"Dear {owner.username}, \n\nYour hotel {hotel.name} has been successfully removed from our platform. If this was a mistake, please contact support.\n\nBest regards,\nYour Hotel Management Team."
        
        # Use background task to send the email
        background_tasks.add_task(send_email, hotel.email, subject, body)

        return f"Hotel with ID {id} deleted successfully."  # Return success message
    else:
        return None  # Return None if hotel not found


def combined_search_filter(
    db: Session,
    search_term: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Dbhotel)

    # Search
    if search_term:
        pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Dbhotel.name.ilike(pattern),
                Dbhotel.location.ilike(pattern),
                Dbhotel.description.ilike(pattern),
            )
        )
    if location:
        query = query.filter(Dbhotel.location.ilike(f"%{location.strip()}%"))

    return query.offset(skip).limit(limit).all()


def get_all_hotels(db: Session):
    return db.query(Dbhotel).all()


def get_hotel(db: Session, id: int):
    return db.query(Dbhotel).filter(Dbhotel.id == id).first()


def update_hotel(db: Session, id: int, request: HotelBase):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()

    if not hotel:
        return None

    hotel.name = request.name
    hotel.description = request.description
    hotel.img_link = request.img_link
    hotel.is_active = request.is_active
    hotel.is_approved = request.is_approved
    hotel.location = request.location
    hotel.phone_number = request.phone_number
    hotel.email = request.email

    db.commit()
    db.refresh(hotel)
    return hotel
