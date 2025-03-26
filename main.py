from fastapi import FastAPI
from routers import hotel, user, booking
from db import models
from db.database import engine

app = FastAPI()
app.include_router(user.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Booking API!!!!"}


app.include_router(hotel.router)

app.include_router(booking.router)  

models.Base.metadata.create_all(engine)
