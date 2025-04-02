from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.oauth2 import create_access_token, get_current_user
from db.database import get_db
from schemas import TokenResponse, UserBase, UpdateUserResponse
from db.Hash import Hash
from db import db_user
from db.models import Dbuser
import re


router = APIRouter(prefix="/user", tags=["user"])
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,}$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

# Validate username format
def validate_username(username: str):
    if not re.match(USERNAME_REGEX, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username format. Only letters, numbers, and underscores allowed (min 3 characters).",
        )
    
# Validate password format
def validate_password(password: str):
    if not re.match(PASSWORD_REGEX, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password format. Must be at least 8 characters long, including an uppercase letter, lowercase letter, number, and special character.",
        )


@router.post("/register")
def register_user(request: UserBase, db: Session = Depends(get_db)):
    # Validate username format
    validate_username(request.username)

    # Validate password format
    validate_password(request.password)

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


# Update user
@router.put("/{username}/update")
def update_user(
    username: str,
    request: UserBase,
    db: Session = Depends(get_db),
    auth_user: Dbuser = Depends(get_current_user),
):
    
    user = db_user.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if auth_user.id != user.id and not auth_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this user"
        )
    
    # Validate username format
    validate_username(request.username)

    # Validate password format
    validate_password(request.password)

    # Check if the username already exists in the database
    existing_user = db_user.get_user_by_username(db, request.username)
    if existing_user and existing_user.id != auth_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken."
        )
    
    # Check if email is already in use by another user
    existing_email_user = db_user.get_user_by_email(db, request.email)
    if existing_email_user and existing_email_user.id != auth_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email is already taken by another user.",
        )


    updated_user = db_user.update_user(db, username, request)

    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update user")

    return UpdateUserResponse(
        message="User updated successfully", user=updated_user
    )