from sqlalchemy.orm import Session
from db.models import Dbhotel, IsActive
from schemas import HotelBase
from sqlalchemy import or_, and_
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status


def create_hotel(db: Session, request: HotelBase):
    new_hotel = Dbhotel(
        name=request.name,
        location=request.location,
        description=request.description,
        price=request.price,
        img_link=request.img_link,
        # user_id=user_id  #store the user who submitted
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel


# delete hotel
def delete_hotel(db: Session, id: int):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with {id} not found")
    hotel.is_active = IsActive.DELETED
    db.commit()
    return "ok"


def search_hotels(db: Session, search_term: str = None):
    query = db.query(Dbhotel)  # Removed: .filter(Dbhotel.is_approved == True)
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Dbhotel.name.ilike(search_pattern),
                Dbhotel.location.ilike(search_pattern),
                Dbhotel.description.ilike(search_pattern),
            )
        )
    return query.all()


def filter_hotels(
    db: Session,
    min_price: Decimal = None,
    max_price: Decimal = None,
    location: str = None,
):
    print(
        f"\n⚡ Filter Params Received - min: {min_price}, max: {max_price}, loc: {location}"
    )

    query = db.query(Dbhotel)

    # Price filters
    if min_price is not None:
        print(f"Applying min_price filter: {min_price}")
        query = query.filter(Dbhotel.price >= min_price)
    if max_price is not None:
        print(f"Applying max_price filter: {max_price}")
        query = query.filter(Dbhotel.price <= max_price)

    # Location filter
    if location:
        print(f"Applying location filter: {location}")
        query = query.filter(Dbhotel.location.ilike(f"%{location}%"))

    results = query.all()
    print(f"Found {len(results)} hotels")
    for hotel in results:
        print(f"  - {hotel.name} (${hotel.price}, {hotel.location})")

    return results


def get_all_hotels(db: Session):
    return db.query(Dbhotel).all()


def get_hotel(db: Session, id: int):
    return db.query(Dbhotel).filter(Dbhotel.id == id).first()


def update_hotel(db: Session, id: int, request: HotelBase):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id)
    hotel.update(
        {
            Dbhotel.name: request.name,
            Dbhotel.description: request.description,
            Dbhotel.img_link: request.img_link,
            Dbhotel.is_active: request.is_activate,
            Dbhotel.is_approved: request.is_approved,
            Dbhotel.location: request.location,
            Dbhotel.price: request.price,
        }
    )
    db.commit()
    return "ok"
