from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.oauth2 import create_access_token, get_current_user
from db.database import get_db
from schemas import TokenResponse, UserBase, UpdateUserResponse, UserDisplay, UserUpdate
from db import db_user
from db.models import Dbuser
import re

router = APIRouter(prefix="/user", tags=["user"])

# Validation patterns
USERNAME_REGEX = r"^[a-zA-Z0-9_]{3,50}$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
PHONE_REGEX = r"^\+[1-9]\d{1,14}$"  # E.164 format


def validate_username(username: str):
    if not re.match(USERNAME_REGEX, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be 3-50 characters (letters, numbers, underscores)",
        )


def validate_password(password: str):
    if not re.match(PASSWORD_REGEX, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 8+ chars with uppercase, lowercase, number, and special character",
        )


def validate_phone(phone_number: str):
    if not re.match(PHONE_REGEX, phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone must be in E.164 format (+[country code][number])",
        )


@router.post("/register")
def register_user(request: UserBase, db: Session = Depends(get_db)):
    validate_username(request.username)
    validate_password(request.password)
    validate_phone(request.phone_number)

    if db_user.get_user_by_username(db, request.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username taken")
    if db_user.get_user_by_email(db, request.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email taken")
    if db_user.get_user_by_phone(db, request.phone_number):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Phone taken")

    new_user = db_user.create_user(db, request)
    return {"id": new_user.id, "username": new_user.username}


@router.post("/login", response_model=TokenResponse)
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db_user.get_user_by_username(db, request.username)
    if not user or not db_user.verify_password(user, request.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/{user_id}", response_model=UpdateUserResponse)
async def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Dbuser = Depends(get_current_user),
):
    # Validate inputs first
    update_data = request.model_dump(exclude_unset=True)
    if "username" in update_data:
        validate_username(update_data["username"])
    if "password" in update_data:
        validate_password(update_data["password"])
    if "phone_number" in update_data:
        validate_phone(update_data["phone_number"])

    # Permission check
    is_admin = current_user.is_superuser
    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    # Get target user's current data
    # Get target user's current data
    target_user = db.query(Dbuser).filter(Dbuser.id == user_id).first()
    if not target_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    # Modified admin role change check
    if (
        "is_superuser" in request.model_dump(exclude_unset=True)
        and request.is_superuser != target_user.is_superuser
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can modify user roles",
        )

    # Define all sensitive fields
    SENSITIVE_FIELDS = [
        "password",
        "email",
        "username",
    ]
    is_updating_sensitive_field = any(
        field in update_data for field in SENSITIVE_FIELDS
    )

    # Check current password requirement for non-admin sensitive changes
    if not is_admin and is_updating_sensitive_field:
        if not request.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required for sensitive field changes",
            )

    try:
        updated_user = db_user.update_user(
            db=db,
            user_id=user_id,
            request=request,
            current_password=request.current_password if not is_admin else None,
            is_admin=is_admin,
        )
    except ValueError as e:
        error_message = str(e)
        if "Current password is incorrect" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )
        elif "User not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request"
        )

    # Handle token regeneration if sensitive fields changed
    response_data = {
        "message": "User updated successfully",
        "user": UserDisplay.from_orm(updated_user),
    }

    if is_updating_sensitive_field:
        response_data.update(
            {"access_token": create_access_token(updated_user), "token_type": "bearer"}
        )

    return response_data
