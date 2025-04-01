from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_room, db_hotel
from db.models import Dbuser
from schemas import RoomBase, RoomDisplay
# from schemas import HotelSearch
from decimal import Decimal
from typing import Optional, List
from auth.oauth2 import get_current_user


router = APIRouter(prefix="/room", tags=["Room"])


@router.post("/submit/{hotel_id}", response_model=RoomDisplay)
def submit_room(
    hotel_id: int,
    request: RoomBase,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),  # Extract logged-in user
):
    """
    Room can be created for the hotel of authenticated user only.
    The owner ID is automatically assigned from the logged-in user.
    """
    hotel = db_hotel.get_hotel(db, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this hotel"
        )

    return db_room.create_room(db, request, hotel_id)  # Now it works