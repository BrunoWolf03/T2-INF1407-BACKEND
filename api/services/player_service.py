from api.models.player import Player

class PlayerService:
    # banco fake só para testar
    players = []
    auto_id = 1

    @classmethod
    def get_all_players(cls):
        return cls.players

    @classmethod
    def create_player(cls, player_data):
        player = Player(
            id=cls.auto_id,
            name=player_data.name,
            score=player_data.score
        )
        cls.players.append(player)
        cls.auto_id += 1
        return player
