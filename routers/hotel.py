from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_hotel
from db.models import Dbuser
from schemas import HotelBase, HotelDisplay
from schemas import HotelSearch
from decimal import Decimal
from typing import Optional, List
from auth.oauth2 import get_current_user


router = APIRouter(prefix="/hotel", tags=["Hotel"])


@router.post("/submit", response_model=HotelDisplay)
def submit_hotel(
    request: HotelBase,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),  # Extract logged-in user
):
    """
    Only authenticated users can create hotels.
    The owner ID is automatically assigned from the logged-in user.
    """
    return db_hotel.create_hotel(db, request, owner_id=user.id)  # Now it works


# read one hotel
@router.get("/{id}", response_model=HotelDisplay)
def get_hotel(id: int, db: Session = Depends(get_db)):
    hotel = db_hotel.get_hotel(db, id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


# Combine search and filter logic into one endpoint
@router.get(
    "/", description="Get filtered/searched hotels ", response_model=List[HotelDisplay]
)
def get_hotels(
    search_term: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    location: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    # Convert to Decimal (if values exist)
    min_dec = Decimal(str(min_price)) if min_price is not None else None
    max_dec = Decimal(str(max_price)) if max_price is not None else None

    # Use the COMBINED function (from db_hotel.py)
    return db_hotel.combined_search_filter(
        db,
        search_term=search_term,
        min_price=min_dec,
        max_price=max_dec,
        location=location.strip() if location else None,
        skip=0,  # Hardcode or make optional
        limit=100,  # Default limit
    )


# update hotels
@router.post("/{id}/update")
def update_hotel(
    id: int,
    request: HotelBase,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    hotel = db_hotel.get_hotel(db, id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this hotel"
        )

    return db_hotel.update_hotel(db, id, request)


### DELETE HOTEL (Only Owner or Super Admin)
@router.delete(
    "/{id}/delete",
    tags=["Hotel"],
    summary="Remove hotel",
    description="Only owner or super admin can delete",
)
def delete_hotel(
    id: int,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),  # Extract logged-in user
):
    """
    Only the owner or a super admin can delete a hotel.
    """
    hotel = db_hotel.get_hotel(db, id)

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this hotel"
        )

    return db_hotel.delete_hotel(db, id)
