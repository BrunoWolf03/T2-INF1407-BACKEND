from api.database.connection import SessionLocal
from api.models.player import Player
from api.schemas.player_schema import PlayerSchema
from sqlalchemy import func
from api.services.balldontlie_service import BallDontLieService

class PlayerService:

    @staticmethod
    def get_all_players():
        db = SessionLocal()
        players = db.query(Player).all()
        db.close()
        return players

    @staticmethod
    def get_player_by_name(db, name: str):
        return (
            db.query(Player)
            .filter(func.lower(Player.name) == name.lower())
            .first()
        )

    @staticmethod
    def update_players():
        page = 1
        total_inserted = 0
        db = SessionLocal()

        while True:
            data = BallDontLieService.get_players(page=page, per_page=100)

            if not data or "data" not in data:
                break

            players = data["data"]
            if not players:
                break

            for p in players:
                name = f"{p['first_name']} {p['last_name']}"
                position = p.get("position", "")
                team = p["team"]["full_name"] if p.get("team") else ""

                if db.query(Player).filter(Player.name == name).first():
                    continue

                new_player = Player(
                    name=name,
                    position=position,
                    team=team,
                    score=0
                )
                db.add(new_player)
                total_inserted += 1

            db.commit()
            page += 1

        db.close()
        print(f"Jogadores inseridos: {total_inserted}")
        return total_inserted
