from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Dbuser, Dbhotel, Dbbooking, Dbreview
from schemas import ReviewBase, ReviewShow
from db import db_review
from typing import List
from datetime import date
from auth.oauth2 import get_current_user


router = APIRouter(
    prefix="/review",
    tags=["Review"]
)
#-------------------------------------------------------------------------------------------------
# submiting a review

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReviewShow)
def submit_review(request: ReviewBase, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(Dbuser).filter(Dbuser.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if hotel exists
    hotel = db.query(Dbhotel).filter(Dbhotel.id == request.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Check if booking exists
    booking = db.query(Dbbooking).filter(Dbbooking.id == request.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Validate that the booking belongs to the user
    if booking.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="You can only review your own bookings.")

    # Validate that the booking is for the same hotel
    if booking.hotel_id != request.hotel_id:
        raise HTTPException(status_code=400, detail="Booking does not match this hotel.")

    # Ensure the checkout date has passed
    if booking.check_out_date >= date.today():
        raise HTTPException(status_code=400, detail="You can only review after your stay has ended.")

    # Check if a review already exists for this booking
    existing_review = db.query(Dbreview).filter(Dbreview.booking_id == request.booking_id).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Review for this booking already exists.")

    # All validations passed → create the review
    return db_review.create_review(db, request)

#-------------------------------------------------------------------------------------------------
# getting all reviews and ratings for specific user id
# so if user logged in as an admin user , can pass any user_id as path parameter to view all reviews and ratings for that user_id
# and normal users just pass their user_id to view just thier reviews and ratings
@router.get("/my-reviews/{user_id}", response_model=List[ReviewShow], summary="ADMIN / Get bookings by User ID",
)
def get_my_reviews(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user)
):
    # to Check if the logged-in user is admin or user_id that is passed as a path parameter matches the requested user_id
    if current_user.is_superuser or current_user.id == user_id:
        return db_review.get_all_reviews_by_user(db, user_id)
    else :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view other users' reviews."
        )
#-------------------------------------------------------------------------------------------------

