from sqlalchemy.orm import Session
from db.models import Dbroom, IsActive
from schemas import RoomBase, RoomUpdate
from sqlalchemy import or_, and_
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status





# Create room
def create_room(db: Session, request: RoomBase, hotel_id: int):
    new_room = Dbroom(
        hotel_id=hotel_id,  # Now store the user who submitted the hotel
        room_number=request.room_number,
        description=request.description,
        price_per_night=request.price_per_night,
        is_active=IsActive.active,
        wifi = request.wifi,
        tv = request.tv,
        air_conditioner = request.air_conditioner,
        status = request.status,
        bed_count = request.bed_count    
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


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
