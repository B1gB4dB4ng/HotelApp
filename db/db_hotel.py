from sqlalchemy.orm import Session
from db.models import Dbhotel, IsActive
from schemas import HotelBase
from sqlalchemy import or_, and_
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status


def create_hotel(db: Session, request: HotelBase, owner_id: int):
    new_hotel = Dbhotel(
        name=request.name,
        location=request.location,
        description=request.description,
        price=request.price,
        img_link=request.img_link,
        owner_id=owner_id,  # Now store the user who submitted the hotel
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel


# delete hotel
def delete_hotel(db: Session, id: int):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Hotel with {id} not found"
        )
    hotel.is_active = IsActive.deleted
    db.commit()
    return "ok"


def combined_search_filter(
    db: Session,
    search_term: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
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

    # Filters
    if min_price is not None:
        query = query.filter(Dbhotel.price >= min_price)
    if max_price is not None:
        query = query.filter(Dbhotel.price <= max_price)
    if location:
        query = query.filter(Dbhotel.location.ilike(f"%{location.strip()}%"))

    return query.offset(skip).limit(limit).all()


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
            Dbhotel.is_active: request.is_active,
            Dbhotel.is_approved: request.is_approved,
            Dbhotel.location: request.location,
            Dbhotel.price: request.price,
        }
    )
    db.commit()
    return "ok"
