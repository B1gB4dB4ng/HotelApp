from sqlalchemy.orm import Session
from db.models import Dbhotel
from schemas import HotelBase
from fastapi import HTTPException, status

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

#delete hotel
def delete_hotel(db: Session, id: int):
    hotel = db.query(Dbhotel).filter(Dbhotel.id == id).first()
    if not hotel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with {id} not found")
    db.delete(hotel)
    db.commit()
    return "ok"
