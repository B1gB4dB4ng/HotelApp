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
        name=request.name,
        description=request.description,
        price=request.price,
        img_link=request.img_link,
        hotel_id=hotel_id,  
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room