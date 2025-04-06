from sqlalchemy.orm import Session
from db.models import Dbhotel, IsActive
from schemas import HotelBase
from sqlalchemy import or_
from typing import Optional


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
def delete_hotel(db: Session, id: int):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()

    if hotel:
        hotel.is_active = IsActive.deleted  # Mark hotel as deleted
        db.commit()
        return f"Hotel with ID {id} deleted successfully."  # Return success message
    else:
        return None  # Return None if hotel not found


def combined_search_filter(
    db: Session,
    search_term: Optional[str] = None,
    location: Optional[str] = None,
    is_approved: Optional[bool] = None,
    owner_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Dbhotel)

    if is_approved is not None:
        query = query.filter(Dbhotel.is_approved == is_approved)

    if owner_id is not None:
        query = query.filter(Dbhotel.owner_id == owner_id)

    # Search term filter
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

# approve hotel
def approve_hotel_by_id(db: Session, id: int):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()

    if hotel.is_approved == False:
        hotel.is_approved = True
    else:
        hotel.is_approved = False
    db.commit()
    db.refresh(hotel)
    return hotel
