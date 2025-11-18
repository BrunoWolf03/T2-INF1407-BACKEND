from fastapi import FastAPI
from api.routers.players import router as players_router
from api.routers.auth import router as auth_router
from api.database.connection import Base, engine, SessionLocal
from api.models.player import Player
from api.services.player_service import PlayerService

app = FastAPI(
    title="Player API",
    version="1.0.0",
)

# Cria tabelas
Base.metadata.create_all(bind=engine)

# Rotas
app.include_router(players_router, prefix="/players", tags=["Players"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])


@app.on_event("startup")
def startup_event():
    print("Iniciando API...")

    db = SessionLocal()
    existing_players = db.query(Player).count()
    db.close()

    if existing_players == 0:
        print("🔄 Base vazia — populando jogadores com BallDontLie...")
        PlayerService.update_players()
        print("✅ Base populada com sucesso!")
    else:
        print(f"✔ Base já possui {existing_players} jogadores — não será repopolada.")


@app.get("/")
def root():
    return {"message": "API is running!"}
