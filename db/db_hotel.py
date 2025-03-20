from db.models import Dbhotel, Dbuser
from sqlalchemy.orm.session import Session

from schemas import HotelBase


def create_hotel(db: Session, request: HotelBase):
    # Find user by username Since we dont have auth yet it is better to filter by username for owner_username
    # We will refactor this after we implement auth
    owner = db.query(Dbuser).filter(Dbuser.username == request.owner_username).first()

    if not owner:
        raise Exception("User not found.")  # Replace with HTTPException in FastAPI

    # Create hotel with owner_id instead of username
    new_hotel = Dbhotel(
        title=request.title,
        description=request.description,
        img_link=request.img_link,
        price=request.price,
        location=request.location,
        is_active=request.is_active,
        
        owner_id=owner.id,
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)

    return new_hotel
