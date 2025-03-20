# from db.models import Dbhotel
# from sqlalchemy.orm.session import Session

# def create_hotel(db: Session, request: HotelBase):
#     new_hotel = Dbhotel(
#         title=request.title,
#         description=request.description,
#         img_link=request.img_link,
#         price=request.price,
#         location=request.location,
#         is_active=request.is_active,
#         owner_username=request.owner_username,
#     )
#     db.add(new_hotel)
#     db.commit()
#     db.refresh(new_hotel)

#     return new_hotel
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
        #user_id=user_id  #store the user who submitted
    )
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel
