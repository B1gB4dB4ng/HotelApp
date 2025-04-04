from sqlalchemy.orm import Session
from db.models import Dbpayment, IsPaymentStatus
from schemas import PaymentBase
from datetime import date
from db.database import get_db


def create_payment(db: Session, payment: PaymentBase, user_id: int):
    db_payment = Dbpayment(
        user_id=user_id,
        booking_id=payment.booking_id,
        amount=payment.amount,
        status=payment.status,
        payment_date=payment.payment_date,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_booking(db: Session, booking_id: int):
    return db.query(Dbpayment).filter(Dbpayment.booking_id == booking_id).first()

def get_payments_by_user(db: Session, user_id: int):
    return db.query(Dbpayment).filter(Dbpayment.user_id == user_id).all()