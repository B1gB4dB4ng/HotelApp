from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_room, db_hotel
from db.models import Dbuser, Dbhotel, Dbroom
from schemas import RoomBase, RoomDisplay, RoomUpdate
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



@router.delete("/{hotel_id}/{room_id}", summary="Soft-delete a room")
def delete_room(
    hotel_id: int,
    room_id: int,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    # Authorization: Only hotel owner or admin can delete
    hotel = db_hotel.get_hotel(db, hotel_id)
    if not hotel or (hotel.owner_id != user.id and not user.is_superuser):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    deleted_room = db_room.delete_room(db, room_id, hotel_id)
    if not deleted_room:
        raise HTTPException(status_code=404, detail="Room not found or already deleted")
    return {"message": f"Room {room_id} deleted"}


@router.put("/{room_id}", response_model=RoomDisplay)
@router.put("/{room_id}", response_model=RoomDisplay)
def update_room(
    room_id: int,
    request: RoomUpdate,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    # First get the room to check hotel ownership
    room = db_room.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Verify user owns the hotel or is admin
    hotel = db.query(Dbhotel).filter(Dbhotel.id == room.hotel_id).first()
    if not hotel or (hotel.owner_id != user.id and not user.is_superuser):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Perform update
    updated_room = db_room.update_room(db, room_id, request)
    if not updated_room:
        raise HTTPException(status_code=400, detail="Update failed")
    
    return updated_room


@router.get("/{hotel_id}", response_model=List[RoomDisplay], summary="List rooms in a hotel")
def list_rooms(
    hotel_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    rooms = db_room.get_rooms_by_hotel(db, hotel_id, status=status)
    if not rooms:
        raise HTTPException(status_code=404, detail="No rooms found")
    return rooms