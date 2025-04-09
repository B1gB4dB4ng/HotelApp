from fastapi import APIRouter, Depends, status, HTTPException, Query, Body
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Dbuser, Dbhotel, Dbbooking, Dbreview
from schemas import ReviewBase, ReviewShow, ReviewUpdate, IsReviewStatus,ReviewCreate,IsReviewStatusSearch
from db import db_review
from typing import List, Optional
from datetime import date
from auth.oauth2 import get_current_user
from sqlalchemy import func
from datetime import date


router = APIRouter(prefix="/review", tags=["Review"])
# -------------------------------------------------------------------------------------------------
# submiting a review

@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=ReviewShow
)
def submit_review(
    request: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    # Check if user exists
    user = db.query(Dbuser).filter(Dbuser.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only the current user can submit review
    if current_user.id != request.user_id:
        raise HTTPException(
            status_code=403, detail="You cannot submit a review for another user."
        )
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
        raise HTTPException(
            status_code=403, detail="You can only review your own bookings."
        )

    # Validate that the booking is for the same hotel
    if booking.hotel_id != request.hotel_id:
        raise HTTPException(
            status_code=400, detail="Booking does not match this hotel."
        )

    # Ensure the checkout date has passed
    if booking.check_out_date >= date.today():
        raise HTTPException(
            status_code=400, detail="You can only review after your stay has ended."
        )

    # Check if a review already exists for this booking
    existing_review = (
        db.query(Dbreview).filter(Dbreview.booking_id == request.booking_id).first()
    )
    if existing_review:
        raise HTTPException(
            status_code=400, detail="Review for this booking already exists."
        )

    # All validations passed → create the review
    return db_review.create_review(db=db, request=request)

# -------------------------------------------------------------------------------------------------
# Get the review with review_id

@router.get(
    "/{review_id}",
    response_model=ReviewShow,
    summary="Get the review with review_id",
)
def get_review_with_review_id(
    review_id: int,
    db: Session = Depends(get_db),
):
    # to  check if the review_id is exist or not
    review = db_review.get_review_by_review_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found. ")
    return review
# -------------------------------------------------------------------------------------------------
# getting all reviews and ratings for specific filters(all users)

def validate_rating(value: Optional[float], name: str):
    if value is not None:
        if value < 0 or value > 5:
            raise HTTPException(
                status_code=400, detail=f"{name} must be between 0 and 5."
            )
        if round(value * 10) != value * 10:
            raise HTTPException(
                status_code=400,
                detail=f"{name} must have only one digit after the decimal point (e.g., 3.5, 4.0, 4.1).",
            )
    return value


@router.get("/", response_model=List[ReviewShow])
def filter_reviews(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(
        None, gt=0, description="Filter by user ID (must be a positive integer)"
    ),
    hotel_id: Optional[int] = Query(
        None, gt=0, description="Filter by hotel ID (must be a positive integer)"
    ),
    booking_id: Optional[int] = Query(
        None, gt=0, description="Filter by booking ID (must be a positive integer)"
    ),
    min_rating: Optional[float] = Query(
        None,
        description="Minimum rating (from 1.0 to 5.0, with at most one decimal place like 3.5, 4.0, etc.)",
    ),
    max_rating: Optional[float] = Query(
        None,
        description="Maximum rating (from 1.0 to 5.0, with at most one decimal place like 3.5, 4.0, etc.)",
    ),
    status: Optional[IsReviewStatusSearch] = Query(
        default=None,
        description="Optional filter by review status (pending, confirmed, rejected)",
    ),
    start_date: Optional[date] = Query(
        None, description="Start date for filtering reviews"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering reviews"
    ),
    search: Optional[str] = Query(None, description="Search term in review comments"),
):
    # Existence checks
    if user_id is not None and not db_review.user_exists(db, user_id):
        raise HTTPException(
            status_code=404, detail=f"User with ID {user_id} does not exist."
        )

    if hotel_id is not None and not db_review.hotel_exists(db, hotel_id):
        raise HTTPException(
            status_code=404, detail=f"Hotel with ID {hotel_id} does not exist."
        )

    if booking_id is not None and not db_review.booking_exists(db, booking_id):
        raise HTTPException(
            status_code=404, detail=f"Booking with ID {booking_id} does not exist."
        )

    if user_id is not None and hotel_id is not None:
        if not db_review.review_exists_for_user_and_hotel(db, user_id, hotel_id):
            raise HTTPException(
                status_code=400,
                detail=f"User ID {user_id} does not have any reviews for Hotel ID {hotel_id}.",
            )

    if user_id is not None and booking_id is not None:
        if not db_review.booking_belongs_to_user(db, user_id, booking_id):
            raise HTTPException(
                status_code=400,
                detail=f"Booking ID {booking_id} does not belong to User ID {user_id}.",
            )
        if not db_review.review_exists_for_user_and_booking(db, user_id, booking_id):
            raise HTTPException(
                status_code=400,
                detail=f"User ID {user_id} has not submitted a review for Booking ID {booking_id}.",
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
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )

    # No match
    if not reviews:
        raise HTTPException(
            status_code=404, detail="There are no reviews matching your filters."
        )

    return reviews


# -------------------------------------------------------------------------------------------------
# edit a review


@router.put("/edit", response_model=ReviewShow)
def edit_review(
    user_id: int = Query(..., gt=0, description="User ID must be a positive integer"),
    review_id: int = Query(
        ..., gt=0, description="Review ID must be a positive integer"
    ),
    request: ReviewUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    # Check if review exists
    review = db.query(Dbreview).filter(Dbreview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # Don't allow editing deleted reviews
    if review.status == IsReviewStatus.deleted:
        raise HTTPException(status_code=400, detail="Deleted reviews cannot be edited.")

    # Check if review belongs to provided user or user is super admin
    if not current_user.is_superuser and review.user_id != user_id:
        raise HTTPException(
            status_code=400, detail="Review does not belong to the given user."
        )

    # Check if user exists
    if not db_review.user_exists(db, user_id):
        raise HTTPException(
            status_code=404, detail=f"User with ID {user_id} does not exist."
        )

    # Only admin or owner can edit
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to edit this review."
        )

    # Normal users can only edit pending reviews
    if (
        not current_user.is_superuser
        and review.status.value != IsReviewStatus.pending.value
    ):
        raise HTTPException(
            status_code=400,
            detail="You can only edit reviews that are pending. Contact support for other changes.",
        )

    # Perform the update
    updated_review = db_review.update_review_by_id(
        db=db,
        review_id=review_id,
        new_rating=request.rating,
        new_comment=request.comment,
        new_status=request.status.value
        if current_user.is_superuser and request.status
        else None,  # ✅ Add this
    )

    # 🔄 Reset status to pending if a normal user edits it
    if not current_user.is_superuser:
        review.status = IsReviewStatus.pending

    db.commit()

    # ⭐ If the review is confirmed → update average review score
    if review.status.value == IsReviewStatus.confirmed.value:
        total_rating, count = (
            db.query(func.sum(Dbreview.rating), func.count(Dbreview.rating))
            .filter(
                Dbreview.hotel_id == review.hotel_id,
                Dbreview.status == IsReviewStatus.confirmed.value,
            )
            .first()
        )

        hotel = db.query(Dbhotel).filter(Dbhotel.id == review.hotel_id).first()
        if hotel:
            hotel.avg_review_score = round(total_rating / count, 2) if count else 0.0
            db.commit()

    return review


# -------------------------------------------------------------------------------------------------
# delete review (soft delete)
@router.delete("/delete/{user_id}/{review_id}")
def delete_review(
    user_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can delete reviews.")

    # Fetch the review
    review = db.query(Dbreview).filter(Dbreview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    print("Status:", review.status, type(review.status))
    db.refresh(review)
    # Check if already deleted BEFORE doing anything
    if review.status == IsReviewStatus.deleted:
        raise HTTPException(status_code=400, detail="Review is already deleted.")

    # Soft delete (update status)
    review.status = IsReviewStatus.deleted
    db.commit()

    # Recalculate average review score after deletion
    total_rating, count = (
        db.query(func.sum(Dbreview.rating), func.count(Dbreview.rating))
        .filter(
            Dbreview.hotel_id == review.hotel_id,
            Dbreview.status == IsReviewStatus.confirmed.value,
        )
        .first()
    )

    hotel = db.query(Dbhotel).filter(Dbhotel.id == review.hotel_id).first()
    if hotel:
        hotel.avg_review_score = round(total_rating / count, 2) if count else 0.0
        db.commit()

    return {
        "detail": f"Review with ID {review_id} soft deleted by Admin User {user_id}."
    }
