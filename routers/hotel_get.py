from fastapi import APIRouter
from typing import List

router = APIRouter(
    prefix='/hotel',
    tags=['hotel']
)

# Sample hotel data, later we can retrieve data from a database
hotels = [
    {"id": 1, "name": "Grand Plaza", "location": "New York", "rating": 4.5},
    {"id": 2, "name": "Ocean View", "location": "Miami", "rating": 4.7},
    {"id": 3, "name": "Mountain Lodge", "location": "Denver", "rating": 4.3}
]

@router.get('/all', summary="Retrieve all hotels")
def get_all_hotels():
    return {"hotels": hotels}