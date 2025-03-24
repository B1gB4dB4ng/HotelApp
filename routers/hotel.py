from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_hotel

router = APIRouter(
    prefix="/hotel",
    tags=["hotel"]
)

# Delete Hotel
@router.get("/{id}/delete",
         tags=["hotel"],
         summary="Remove hotel",
         description="This API call removes hotel from db")
def delete(id: int, db: Session = Depends(get_db)):
    return db_hotel.delete_hotel(db, id)