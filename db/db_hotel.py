from db.models import Dbhotel
from sqlalchemy.orm.session import Session

from schemas import HotelBase


def create_hotel(db: Session, request: HotelBase):
    new_hotel = Dbhotel(
        title=request.title,
        description=request.description,
        img_link=request.img_link,
        price=request.price,
        location=request.location,
        is_active=request.is_active,
        owner_username=request.owner_username,
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)

    return new_hotel
