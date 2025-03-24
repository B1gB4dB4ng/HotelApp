from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import UserBase
from db import db_user

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/")
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)
