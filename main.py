from fastapi import FastAPI
from routers import user
from db import models
from db.database import engine

app = FastAPI()
app.include_router(user.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Booking API!!!"}


models.Base.metadata.create_all(engine)
