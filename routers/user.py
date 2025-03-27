from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.oauth2 import create_access_token
from db.database import get_db
from schemas import TokenResponse, UserBase
from db.Hash import Hash
from db import db_user
import re

router = APIRouter(prefix="/user", tags=["user"])
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,}$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


@router.post("/register")
def register_user(request: UserBase, db: Session = Depends(get_db)):
    """Handles user registration with input validation."""

    # Validate username format
    if not re.match(USERNAME_REGEX, request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username format. Only letters, numbers, and underscores allowed (min 3 characters).",
        )

    # Validate password format
    if not re.match(PASSWORD_REGEX, request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password format. Must be at least 8 characters long, including an uppercase letter, lowercase letter, number, and special character.",
        )

    # Check if the username already exists in the database
    existing_user = db_user.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken."
        )

    # Create user if validation passes
    new_user = db_user.create_user(db, request)
    return {"id": new_user.id, "username": new_user.username}


@router.post("/login", response_model=TokenResponse)
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db_user.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username"
        )

    if not Hash.verify(user.hashed_password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    access_token = create_access_token(user=user)

    return {"access_token": access_token, "token_type": "bearer"}
