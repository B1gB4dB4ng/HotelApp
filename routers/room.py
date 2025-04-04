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


# Many time used functions

# if hotel doesn't exist
def ensure_hotel_exist(hotel):
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

# if hotel is not approved
def ensure_hotel_approved(hotel):
    if not hotel.is_approved:
        raise HTTPException(
            status_code=400, detail="Your hotel is not approved. Please contact support for approval."
        )

# if user is not the hotel owner or superuser
def ensure_user_is_owner_or_superuser(hotel, user):
    if hotel.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this hotel"
        )


# ==== Room actions ======

router = APIRouter(prefix="/room", tags=["Room"])

# Add room
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

    ensure_hotel_exist(hotel)
    ensure_user_is_owner_or_superuser(hotel, user)
    ensure_hotel_approved(hotel)
    

    return db_room.create_room(db, request, hotel_id)  # Now it works

