from sqlalchemy.orm.session import Session
from db.Hash import Hash
from db.models import Dbuser
from schemas import UserBase


def create_user(db: Session, request: UserBase):
    new_user = Dbuser(
        username=request.username,
        email=request.email,
        hashed_password=Hash.bcrypt(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_username(db: Session, username: str):
    return db.query(Dbuser).filter(Dbuser.username == username).first()
