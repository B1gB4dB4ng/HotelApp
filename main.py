from fastapi import FastAPI
from router import hotel_get
from db import models
from db.database import engine

from db import models
from db.database import engine

app = FastAPI()
app.include_router(hotel_get.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Booking API!"}


models.Base.metadata.create_all(engine)
