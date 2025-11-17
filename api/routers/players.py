from fastapi import APIRouter
from api.schemas.player_schema import PlayerSchema
from api.services.player_service import PlayerService

router = APIRouter()

@router.get("/", response_model=list[PlayerSchema])
def list_players():
    return PlayerService.get_all_players()

@router.post("/", response_model=PlayerSchema)
def create_player(player: PlayerSchema):
    return PlayerService.create_player(player)
