from fastapi import FastAPI
from api.routers.players import router as players_router

app = FastAPI(
    title="Player API",
    version="1.0.0",
)

app.include_router(players_router, prefix="/players", tags=["Players"])


@app.get("/")
def root():
    return {"message": "API is running!"}
