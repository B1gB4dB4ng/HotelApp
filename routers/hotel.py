from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import HotelBase, HotelDisplay
from db import db_hotel

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"]
)

@router.post("/submit", response_model=HotelDisplay)
def submit_hotel(request: HotelBase, db: Session = Depends(get_db)):
    # For now we'll fake the user ID (you'll replace with real one later)
    #user_id = 1
    return db_hotel.create_hotel(db, request)



