from sqlalchemy.orm import Session
from schemas import ReviewBase
from sqlalchemy import func
from db.models import Dbreview, Dbhotel
from typing import Optional, List


# ------------------------------------------------------------------------------------------
# submit a review
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
    total_rating = (
        db.query(func.sum(Dbreview.rating))
        .filter(Dbreview.hotel_id == request.hotel_id)
        .scalar()
    )

    # Step 3: Calculate and update average
    avg_rating = (
        round(total_rating / rating_count, 2) if rating_count else request.rating
    )

    hotel = db.query(Dbhotel).filter(Dbhotel.id == request.hotel_id).first()
    hotel.avg_review_score = avg_rating
    db.commit()

    return db_review


# ------------------------------------------------------------------------------------------
# def get_all_reviews_by_user(db: Session, user_id: int):
#     return db.query(Dbreview).filter(Dbreview.user_id == user_id).all()


# ------------------------------------------------------------------------------------------
# get review by id
def get_review_by_review_id(db: Session, review_id: int):
    return db.query(Dbreview).filter(Dbreview.id == review_id).first()


# ------------------------------------------------------------------------------------------
# get reviewa by filtering
def get_filtered_reviews(
    db: Session,
    user_id: Optional[int] = None,
    hotel_id: Optional[int] = None,
    booking_id: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    status: Optional[str] = None,
) -> List[Dbreview]:
    query = db.query(Dbreview)

    if user_id is not None:
        query = query.filter(Dbreview.user_id == user_id)

    if hotel_id is not None:
        query = query.filter(Dbreview.hotel_id == hotel_id)

    if booking_id is not None:
        query = query.filter(Dbreview.booking_id == booking_id)

    if min_rating is not None:
        query = query.filter(Dbreview.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(Dbreview.rating <= max_rating)

    if status is not None:
        query = query.filter(Dbreview.status == status)

    return query.all()


# Helper functions for existence checks
def user_exists(db: Session, user_id: int) -> bool:
    from db.models import Dbuser

    return db.query(Dbuser).filter(Dbuser.id == user_id).first() is not None


def hotel_exists(db: Session, hotel_id: int) -> bool:
    from db.models import Dbhotel

    return db.query(Dbhotel).filter(Dbhotel.id == hotel_id).first() is not None


def booking_exists(db: Session, booking_id: int) -> bool:
    from db.models import Dbbooking

    return db.query(Dbbooking).filter(Dbbooking.id == booking_id).first() is not None


def review_exists_for_user_and_hotel(db: Session, user_id: int, hotel_id: int) -> bool:
    return (
        db.query(Dbreview)
        .filter(Dbreview.user_id == user_id, Dbreview.hotel_id == hotel_id)
        .first()
        is not None
    )


def review_exists_for_user_and_booking(
    db: Session, user_id: int, booking_id: int
) -> bool:
    return (
        db.query(Dbreview)
        .filter(Dbreview.user_id == user_id, Dbreview.booking_id == booking_id)
        .first()
        is not None
    )


def booking_belongs_to_user(db: Session, user_id: int, booking_id: int) -> bool:
    from db.models import Dbbooking

    return (
        db.query(Dbbooking)
        .filter(Dbbooking.id == booking_id, Dbbooking.user_id == user_id)
        .first()
        is not None
    )


# ------------------------------------------------------------------------------------------
# update a review
def update_review_by_id(
    db: Session, review_id: int, new_rating: Optional[float], new_comment: Optional[str]
) -> Dbreview:
    review_query = db.query(Dbreview).filter(Dbreview.id == review_id)

    review = review_query.first()
    if not review:
        return None

    update_data = {}
    if new_rating is not None:
        update_data["rating"] = new_rating
    if new_comment is not None:
        update_data["comment"] = new_comment

    review_query.update(update_data)
    db.commit()
    return review_query.first()


# ------------------------------------------------------------------------------------------
# delet a review
def soft_delete_review_by_id(db: Session, review_id: int):
    review = db.query(Dbreview).filter(Dbreview.id == review_id).first()
    if review:
        review.status = "deleted"
        db.commit()
    return review
