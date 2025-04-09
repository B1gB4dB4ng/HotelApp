from fastapi import APIRouter, Depends, HTTPException, Path,Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import PaymentCreate, PaymentShow,PaymentStatus
from db import db_payment
from auth.oauth2 import get_current_user
from db.models import Dbuser, Dbbooking,Dbpayment
from decimal import Decimal
from typing import List, Optional
from datetime import date



router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/{user_id}", response_model=PaymentShow)
def make_payment_for_user(
    user_id: int,
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to pay for another user.")

    # Always successful payment
    payment_status = PaymentStatus.completed

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
    "/{payment_id}",
    response_model=PaymentShow,
    summary="Get the payment with Payment_id",
)
def get_payment_with_payment_id(
    payment_id: int = Path(..., gt=0, description="Payment ID must be a positive integer"),
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    payment = db_payment.get_payment_by_payment_id(db, payment_id)

    # Check if the payment exists
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")

    # Check if the payment belongs to the current user or user is super admin
    if payment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")

    return payment

#-------------------------------------------------------------------------------------------
@router.get("/", response_model=List[PaymentShow], summary="Search all payments (superadmin only)")
def search_payments_superadmin_only(
    status: Optional[PaymentStatus] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, gt=0, description="User ID"),
    start_date: Optional[date] = Query(None, description="Start of payment date"),
    end_date: Optional[date] = Query(None, description="End of payment date"),
    min_amount: Optional[Decimal] = Query(None, gt=0, description="Minimum amount"),
    max_amount: Optional[Decimal] = Query(None, gt=0, description="Maximum amount"),
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    # 🔐 Superadmin-only access check
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied. Superadmin only.")

    query = db.query(Dbpayment)

    # ✅ Apply optional filters
    if user_id:
        query = query.filter(Dbpayment.user_id == user_id)

    if status:
        query = query.filter(Dbpayment.status == status.value)

    if start_date:
        query = query.filter(Dbpayment.payment_date >= start_date)

    if end_date:
        query = query.filter(Dbpayment.payment_date <= end_date)

    if min_amount and max_amount and min_amount > max_amount:
        raise HTTPException(status_code=400, detail="min_amount cannot be greater than max_amount")

    if min_amount:
        query = query.filter(Dbpayment.amount >= min_amount)

    if max_amount:
        query = query.filter(Dbpayment.amount <= max_amount)

    results = query.all()
     #If no payments found, raise 404 with custom message
    if not results:
        raise HTTPException(status_code=404, detail="No matching payments found.")

    return results
