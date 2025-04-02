from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import Dbreview 
from schemas import ReviewBase
from sqlalchemy import func
from db.models import Dbreview, Dbhotel

def create_review(db: Session, request: ReviewBase):
    # Step 1: Save the review
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

    # Step 2: Recalculate average rating for the hotel
    # Get all existing ratings for the hotel (excluding the new one just added)
    ratings_query = db.query(Dbreview).filter(Dbreview.hotel_id == request.hotel_id)
    rating_count = ratings_query.count()
    total_rating = db.query(func.sum(Dbreview.rating)).filter(Dbreview.hotel_id == request.hotel_id).scalar()

    # Step 3: Calculate and update average
    avg_rating = round(total_rating / rating_count, 2) if rating_count else request.rating

    hotel = db.query(Dbhotel).filter(Dbhotel.id == request.hotel_id).first()
    hotel.avg_review_score = avg_rating
    db.commit()
    


    return db_review
#------------------------------------------------------------------------------------------
def get_all_reviews_by_user(db: Session, user_id: int):
    return db.query(Dbreview).filter(Dbreview.user_id == user_id).all()

#------------------------------------------------------------------------------------------
def get_all_reviews_by_user(db: Session, user_id: int):
    return db.query(Dbreview).filter(Dbreview.user_id == user_id).all()

