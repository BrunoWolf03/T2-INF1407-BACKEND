from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.models.player import Player
from api.schemas.player_schema import PlayerCreate, PlayerResponse

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)


@router.post("/", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    # Verifica se o jogador já existe
    existing = db.query(Player).filter(Player.id == player.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Player already exists.")

    # Cria o objeto SQLAlchemy
    new_player = Player(
        id=player.id,
        first_name=player.first_name,
        last_name=player.last_name,
        position=player.position,
        team=player.team
    )

    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    return new_player


@router.get("/", response_model=list[PlayerResponse])
def list_players(db: Session = Depends(get_db)):
    players = db.query(Player).all()
    return players


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player
