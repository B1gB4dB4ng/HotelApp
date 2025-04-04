from sqlalchemy.orm import Session
from db.models import Dbroom, IsActive, Dbbooking, Dbhotel, IsRoomStatus    
from schemas import RoomBase, RoomUpdate, RoomCreate
from sqlalchemy import or_, and_, not_
from decimal import Decimal
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from datetime import date 



# Create room
def create_room(db: Session, request: RoomCreate) -> Dbroom:
    # Check for duplicate room number in the same hotel
    existing_room = db.query(Dbroom).filter(
        Dbroom.room_number == request.room_number,
        Dbroom.hotel_id == request.hotel_id,
        Dbroom.is_active != "deleted"
    ).first()
    
    if existing_room:
        raise HTTPException(
            status_code=400,
            detail="Room number already exists in this hotel"
        )

    try:
        new_room = Dbroom(**request.dict())
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return new_room
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )

# Delete a Room
def delete_room(db: Session, room_id: int, hotel_id: int):
    room = db.query(Dbroom).filter(
        Dbroom.id == room_id,
        Dbroom.hotel_id == hotel_id,
        Dbroom.is_active == IsActive.active  # Only delete active rooms
    ).first()
    if not room:
        return None
    room.is_active = IsActive.deleted
    db.commit()
    return room


# Update a Room
def update_room(db: Session, room_id: int, request: RoomUpdate):
    room = db.query(Dbroom).filter(Dbroom.id == room_id).first()
    if not room:
        return None
    
    # Update only provided fields
    for field, value in request.dict(exclude_unset=True).items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    return room

def get_room(db: Session, room_id: int):
    return db.query(Dbroom).filter(Dbroom.id == room_id).first()

# Filter a Room
def get_rooms_by_hotel(
    db: Session,
    hotel_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,  # Filter by status (e.g., "available")
):
    query = db.query(Dbroom).filter(
        Dbroom.hotel_id == hotel_id,
        Dbroom.is_active == IsActive.active
    )
    if status:
        query = query.filter(Dbroom.status == status)
    return query.offset(skip).limit(limit).all()


# Room Search functionality
def advanced_room_search(
    db: Session,
    search_term: Optional[str] = None,
    wifi: Optional[bool] = None,
    air_conditioner: Optional[bool] = None,
    tv: Optional[bool] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    check_in_date: Optional[date] = None,
    check_out_date: Optional[date] = None,
) -> List[Dbroom]:
    query = db.query(Dbroom).filter(Dbroom.is_active == IsActive.active)

    # Text search
    if search_term:
        pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Dbroom.room_number.ilike(pattern),
                Dbroom.description.ilike(pattern),
            )
        )

    # Filter by amenities
    if wifi is not None:
        query = query.filter(Dbroom.wifi == wifi)
    if air_conditioner is not None:
        query = query.filter(Dbroom.air_conditioner == air_conditioner)
    if tv is not None:
        query = query.filter(Dbroom.tv == tv)

    # Filter by price
    if min_price is not None:
        query = query.filter(Dbroom.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Dbroom.price_per_night <= max_price)

    # Exclude already booked rooms during the selected date range
    if check_in_date and check_out_date:
        overlapping_room_ids = [
            booking.room_id
            for booking in db.query(Dbbooking)
            .filter(
                Dbbooking.is_active == IsActive.active,
                Dbbooking.check_in_date < check_out_date,
                Dbbooking.check_out_date > check_in_date,
            )
            .all()
        ]

        if overlapping_room_ids:
            query = query.filter(~Dbroom.id.in_(overlapping_room_ids))

    return query.all()