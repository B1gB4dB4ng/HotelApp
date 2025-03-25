from fastapi import FastAPI
from auth import authentication
from routers import hotel, user
from db import models
from db.database import engine

app = FastAPI()
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(hotel.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Booking API!!!"}


models.Base.metadata.create_all(engine)
