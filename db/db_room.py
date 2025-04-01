from sqlalchemy.orm import Session
from db.models import Dbroom, IsActive
from schemas import RoomBase
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