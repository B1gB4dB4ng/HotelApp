from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Dbuser, Dbhotel, Dbbooking, Dbreview
from schemas import ReviewBase, ReviewShow
from db import db_review
from typing import List, Optional
from datetime import date
from auth.oauth2 import get_current_user


router = APIRouter(
    prefix="/review",
    tags=["Review"]
)
#-------------------------------------------------------------------------------------------------
# submiting a review

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReviewShow)
def submit_review(request: ReviewBase, db: Session = Depends(get_db), current_user: Dbuser = Depends(get_current_user),):
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
# Get the review with review_id
@router.get("/{review_id}", response_model = ReviewShow, summary="Get the review with review_id",)
def get_review_with_review_id(
    review_id : int,
    db: Session = Depends(get_db),
):
    # to  check if the review_id is exist or not
    review = db_review.get_review_by_review_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found. ")
    return review
#-------------------------------------------------------------------------------------------------
# getting all reviews and ratings for specific filters(all users)
def validate_rating(value: Optional[float], name: str):
    if value is not None:
        if value < 0 or value > 5:
            raise HTTPException(status_code=400, detail=f"{name} must be between 0 and 5.")
        if round(value * 10) != value * 10:
            raise HTTPException(
                status_code=400,
                detail=f"{name} must have only one digit after the decimal point (e.g., 3.5, 4.0, 4.1)."
            )
    return value

@router.get("/", response_model=List[ReviewShow])
def filter_reviews(
    db: Session = Depends(get_db),
    #current_user: Dbuser = Depends(get_current_user),
    user_id: Optional[int] = Query(None, gt=0, description="Must be a positive integer"),
    hotel_id: Optional[int] = Query(None, gt=0, description="Must be a positive integer"),
    booking_id: Optional[int] = Query(None, gt=0, description="Must be a positive integer"),
    min_rating: Optional[float] = Query(None),
    max_rating: Optional[float] = Query(None),
):
    # Existence checks
    if user_id is not None and not db_review.user_exists(db, user_id):
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} does not exist.")

    if hotel_id is not None and not db_review.hotel_exists(db, hotel_id):
        raise HTTPException(status_code=404, detail=f"Hotel with ID {hotel_id} does not exist.")

    if booking_id is not None and not db_review.booking_exists(db, booking_id):
        raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} does not exist.")

    
    if user_id is not None and hotel_id is not None:
        if not db_review.review_exists_for_user_and_hotel(db, user_id, hotel_id):
            raise HTTPException(
                status_code=400,
                detail=f"User ID {user_id} does not have any reviews for Hotel ID {hotel_id}."
            )

    
    if user_id is not None and booking_id is not None:
        if not db_review.booking_belongs_to_user(db, user_id, booking_id):
            raise HTTPException(
                status_code=400,
                detail=f"Booking ID {booking_id} does not belong to User ID {user_id}."
            )
        if not db_review.review_exists_for_user_and_booking(db, user_id, booking_id):
            raise HTTPException(
                status_code=400,
                detail=f"User ID {user_id} has not submitted a review for Booking ID {booking_id}."
            )

    # Validate rating format
    min_rating = validate_rating(min_rating, "min_rating")
    max_rating = validate_rating(max_rating, "max_rating")

    # Fetch reviews
    reviews = db_review.get_filtered_reviews(
        db=db,
        user_id=user_id,
        hotel_id=hotel_id,
        booking_id=booking_id,
        min_rating=min_rating,
        max_rating=max_rating,
    )

    # No match
    if not reviews:
        raise HTTPException(status_code=404, detail="There are no reviews matching your filters.")

    return reviews