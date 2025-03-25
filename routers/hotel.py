from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_hotel
from schemas import HotelBase, HotelDisplay
from auth.oauth2 import oauth2_scheme


router = APIRouter(prefix="/hotel", tags=["Hotel"])

# You should use delete decorator instead of get
# In common practice ,it is better actually not delete it from DB but update(patch) or using post to update items as inactive etc


# Delete Hotel
@router.get(
    "/{id}/delete",
    tags=["hotel"],
    summary="Remove hotel",
    description="This API call removes hotel from db",
)
def delete(id: int, db: Session = Depends(get_db)):
    return db_hotel.delete_hotel(db, id)


@router.post("/submit", response_model=HotelDisplay)
def submit_hotel(
    request: HotelBase,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
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
