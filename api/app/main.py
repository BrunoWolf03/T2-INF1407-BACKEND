from fastapi import FastAPI
from api.routers.players import router as players_router

app = FastAPI()

app.include_router(players_router)

@app.get("/")
def root():
    return {"message": "NBA Fantasy API Running"}
