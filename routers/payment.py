from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db 
from schemas import PaymentBase, PaymentShow
from db import db_payment
from auth.oauth2 import get_current_user
from db.models import Dbbooking

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/", response_model=PaymentShow)
def make_payment(payment: PaymentBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Make sure the booking exists and belongs to the current user
    booking = db.query(Dbbooking).filter(Dbbooking.id == payment.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only pay for your own bookings")

    existing_payment = get_payment_by_booking(db, payment.booking_id)
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this booking")

    return create_payment(db, payment, user.id)
