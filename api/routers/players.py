from fastapi import APIRouter
from api.schemas.player_schema import PlayerSchema
from api.services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/", response_model=list[PlayerSchema])
def list_players():
    """Lista todos os jogadores"""
    return PlayerService.get_all_players()


@router.post("/", response_model=PlayerSchema)
def create_player(player: PlayerSchema):
    """Cria um novo jogador"""
    return PlayerService.create_player(player)


@router.post("/update")
def update_players():
    """
    Atualiza jogadores com dados de exemplo.
    """
    updated = PlayerService.update_players()
    return {"message": "Base atualizada!", "total": updated}
