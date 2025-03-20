from fastapi import FastAPI

app = FastAPI()

@app.get("/hotel/delete/{id}")
def delete_hotel(id: int):
    return{"message" : f"The hotel with {id} has been deleted"}