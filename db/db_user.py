from sqlalchemy.orm.session import Session
from db.Hash import Hash
from db.models import Dbuser
from schemas import UserBase


def create_user(db: Session, request: UserBase):
    new_user = Dbuser(
        username=request.username,
        email=request.email,
        hashed_password=Hash.bcrypt(request.password),
        phone_number=request.phone_number,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_username(db: Session, username: str):
    return db.query(Dbuser).filter(Dbuser.username == username).first()

def get_user_by_email(db: Session, user_email: str):
    return db.query(Dbuser).filter(Dbuser.email == user_email).first()

def get_user_by_phone(db: Session, user_phone: str):
    return db.query(Dbuser).filter(Dbuser.phone_number == user_phone).first()

#User Update
def update_user(db: Session, username: str, request: UserBase):
    user = db.query(Dbuser).filter(Dbuser.username == username).first()

    if not user:
        return None

    user.username = request.username
    user.email = request.email
    user.hashed_password=Hash.bcrypt(request.password)
    user.phone_number = request.phone_number

    db.commit()
    db.refresh(user)
    return user