from sqlalchemy.orm import Session
from db.models import Dbhotel
from schemas import HotelBase


def create_hotel(db: Session, request: HotelBase):
    new_hotel = Dbhotel(
        name=request.name,
        location=request.location,
        description=request.description,
        price=request.price,
        img_link=request.img_link,
        # user_id=user_id  #store the user who submitted
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel


# delete hotel
def delete_hotel(db: Session, id: int):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()
    db.delete(hotel)
    db.commit()
    return "ok"


def get_all_hotels(db: Session):
    return db.query(Dbhotel).all()


def get_hotel(db: Session, id: int):
    return db.query(Dbhotel).filter(Dbhotel.id == id).first()


def update_hotel(db: Session, id: int, request: HotelBase):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id)
    hotel.update(
        {
            Dbhotel.name: request.name,
            Dbhotel.description: request.description,
            Dbhotel.img_link: request.img_link,
            Dbhotel.is_active: request.is_activate,
            Dbhotel.is_approved: request.is_approved,
            Dbhotel.location: request.location,
            Dbhotel.price: request.price,
        }
    )
    db.commit()
    return "ok"
