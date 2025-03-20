from fastapi import FastAPI

from db import models
from db.database import engine

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Booking API!"}


models.Base.metadata.create_all(engine)
