from fastapi import APIRouter, Depends, HTTPException
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
@router.get("/{payment_id}", response_model = PaymentShow, summary="Get the payment with Payment_id",)
def get_payment_with_payment_id(
    payment_id : int,
    db: Session = Depends(get_db),
):
    # to  check if the payment_id is exist or not
    payment = db_payment.get_payment_by_payment_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payment not found. ")
    return payment
