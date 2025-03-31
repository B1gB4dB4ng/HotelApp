from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import Dbreview 
from schemas import ReviewBase


router = APIRouter(prefix="/review", tags=["Review"])

def create_review(db: Session, request: ReviewBase):
    db_review = Dbreview(
        user_id=request.user_id,
        hotel_id=request.hotel_id,
        booking_id=request.booking_id,
        rating=request.rating,
        comment=request.comment,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review