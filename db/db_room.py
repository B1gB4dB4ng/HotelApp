from sqlalchemy.orm import Session
from db.models import Dbroom, IsActive, Dbbooking, Dbhotel, IsRoomStatus    
from schemas import RoomBase, RoomUpdate, RoomCreate
from sqlalchemy import or_, and_, not_
from decimal import Decimal
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from datetime import date 

# Create a Room
def create_room(db: Session, request: RoomCreate) -> Dbroom:
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

# Search by a Room Number and a Hotel it
def get_room_by_number(db: Session, room_num: int, hotel_id: int):
    return db.query(Dbroom).filter(Dbroom.room_number == room_num, Dbroom.hotel_id == hotel_id).first()

# Delete a Room
def delete_room(db: Session, room_id: int):
    room = db.query(Dbroom).filter(
        Dbroom.id == room_id,
        Dbroom.is_active == IsActive.active
    ).first()

    if not room:
        return None

    room.is_active = IsActive.deleted
    room.status = IsRoomStatus.unavailable  
    db.commit()
    return room

# Update a Room
def update_room(db: Session, room_id: int, request: RoomUpdate):
    room = db.query(Dbroom).filter(Dbroom.id == room_id).first()
    if not room:
        return None
    for field, value in request.dict(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room

#############
def get_room(db: Session, room_id: int):
    return db.query(Dbroom).filter(Dbroom.id == room_id).first()

def get_rooms_by_hotel(
    db: Session,
    hotel_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Dbroom).filter(
        Dbroom.hotel_id == hotel_id,
        Dbroom.is_active != IsActive.deleted  # ✅ include active/inactive, exclude deleted
    )

    if status:
        query = query.filter(Dbroom.status == status)

    return query.offset(skip).limit(limit).all()



# Search a Room Using Different Filters
def advanced_room_search(
    db: Session,
    hotel_id: Optional[int] = None,
    search_term: Optional[str] = None,
    wifi: Optional[bool] = None,
    air_conditioner: Optional[bool] = None,
    tv: Optional[bool] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    check_in_date: Optional[date] = None,
    check_out_date: Optional[date] = None,
    
) -> List[Dbroom]:
    # Start query by filtering out deleted rooms
    query = db.query(Dbroom).filter(Dbroom.is_active != IsActive.deleted)

    # Filter by hotel_id if provided
    if hotel_id is not None:
        query = query.filter(Dbroom.hotel_id == hotel_id)

    # Search term filter (room number or description)
    if search_term:
        pattern = f"%{search_term.strip()}%"
        query = query.filter(
            or_(
                Dbroom.room_number.ilike(pattern),
                Dbroom.description.ilike(pattern),
            )
        )

    # Boolean filters
    if wifi is not None:
        query = query.filter(Dbroom.wifi == wifi)
    if air_conditioner is not None:
        query = query.filter(Dbroom.air_conditioner == air_conditioner)
    if tv is not None:
        query = query.filter(Dbroom.tv == tv)

    # Price range filters
    if min_price is not None:
        query = query.filter(Dbroom.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Dbroom.price_per_night <= max_price)

    # Date availability filter (exclude rooms already booked)
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
