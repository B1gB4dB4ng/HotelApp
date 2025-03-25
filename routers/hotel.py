from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_hotel
from schemas import HotelBase, HotelDisplay
from schemas import HotelSearch
from decimal import Decimal
from typing import Optional, List


router = APIRouter(prefix="/hotel", tags=["Hotel"])


# Delete Hotel
@router.get(
    "/{id}/delete",
    tags=["Hotel"],
    summary="Remove hotel",
    description="This API call removes hotel from db",
)
def delete(id: int, db: Session = Depends(get_db)):
    return db_hotel.delete_hotel(db, id)


@router.post("/submit", response_model=HotelDisplay)
def submit_hotel(request: HotelBase, db: Session = Depends(get_db)):
    # For now we'll fake the user ID (you'll replace with real one later)
    # user_id = 1
    return db_hotel.create_hotel(db, request)


# read all hotels
@router.get("/all", response_model=list[HotelDisplay])
def get_all_hotels(db: Session = Depends(get_db)):
    return db_hotel.get_all_hotels(db)


# raed one hotel
@router.get("/{id}", response_model=HotelDisplay)
def get_hotel(id: int, db: Session = Depends(get_db)):
    return db_hotel.get_hotel(db, id)


# update hotels
@router.post("/{id}/update")
def update_hotel(id: int, request: HotelBase, db: Session = Depends(get_db)):
    return db_hotel.update_hotel(db, id, request)


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
    # Convert to Decimal only if values exist
    min_dec = Decimal(str(min_price)) if min_price is not None else None
    max_dec = Decimal(str(max_price)) if max_price is not None else None

    # Search first if a search term is provided
    hotels = (
        db_hotel.search_hotels(db, search_term)
        if search_term
        else db_hotel.get_all_hotels(db)
    )

    # Apply filtering if necessary
    if min_price is not None or max_price is not None or location:
        # Filter hotels based on the passed query parameters
        filtered_hotels = db_hotel.filter_hotels(
            db,
            min_price=min_dec,
            max_price=max_dec,
            location=location.strip() if location else None,
        )
        return filtered_hotels

    return hotels
