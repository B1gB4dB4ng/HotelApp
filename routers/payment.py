from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import PaymentBase, PaymentShow
from db import db_payment
from auth.oauth2 import get_current_user
from db.models import Dbuser, Dbbooking
from decimal import Decimal


router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/{user_id}", response_model=PaymentShow)
def make_payment_for_user(
    user_id: int,
    payment: PaymentBase,
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to pay for another user.")

    # Always successful payment
    payment_status = "completed"

    # Get booking and amount
    booking = db.query(Dbbooking).filter(Dbbooking.id == payment.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="This booking doesn't belong to you.")

    total_amount: Decimal = booking.total_cost

    # Save payment
    saved_payment = db_payment.create_payment(
        db, payment, user_id=user_id, status=payment_status, amount=total_amount
    )

    # Update booking status in booking table if payment successful
    if payment_status == "completed":
        booking.status = "confirmed"
        db.commit()

    return saved_payment
#-------------------------------------------------------------------------------------------
# Get the payment with payment_id
@router.get(
    "/user/{user_id}/{payment_id}",
    response_model=PaymentShow,
    summary="Get the payment with Payment_id",
)
def get_payment_with_payment_id(
    user_id: int = Path(..., gt=0, description="User ID must be a positive integer"),
    payment_id: int = Path(..., gt=0, description="Payment ID must be a positive integer"),
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    payment = db_payment.get_payment_by_payment_id(db, payment_id)

    # 1. Check if the payment exists
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")

    # 2. Check if the payment belongs to the provided user_id
    if payment.user_id != user_id:
        raise HTTPException(status_code=400, detail="This payment does not belong to the provided user_id.")

    # 3. Check if the current user is authorized to access it (owner or admin)
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
        status_code=403, detail="Not authorized to view this payment"
    )

    return payment
