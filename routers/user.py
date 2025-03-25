from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.oauth2 import create_access_token
from db.database import get_db
from schemas import  TokenResponse, UserBase
from db.Hash import Hash
from db import db_user

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register")
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)


@router.post("/login", response_model=TokenResponse)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db_user.get_user_by_username(db, request.username)
    if not user or not Hash.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
