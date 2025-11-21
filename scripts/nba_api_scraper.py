"""
NBA Player Photo Fetcher usando a API da NBA Stats
Alternativa mais rápida ao Selenium, usando APIs não oficiais da NBA
"""

import requests
from typing import Optional, Dict, List
from difflib import SequenceMatcher


class NBAAPIFetcher:
    """Busca informações de jogadores usando APIs da NBA"""

    # APIs da NBA
    NBA_STATS_API = "https://stats.nba.com/stats/commonallplayers"
    NBA_PHOTO_CDN = "https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png"
    NBA_PHOTO_CDN_260 = "https://cdn.nba.com/headshots/nba/latest/260x190/{nba_id}.png"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }

    def __init__(self):
        self.players_cache: Dict[str, dict] = {}
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_all_players(self, current_season_only: bool = True) -> List[dict]:
        """
        Busca todos os jogadores da NBA

        Args:
            current_season_only: Se True, retorna apenas jogadores ativos na temporada atual

        Returns:
            Lista de jogadores com suas informações
        """
        params = {
            "LeagueID": "00",
            "Season": "2024-25",
            "IsOnlyCurrentSeason": "1" if current_season_only else "0"
        }

        try:
            response = self.session.get(self.NBA_STATS_API, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Parse da resposta da NBA Stats API
            headers = data['resultSets'][0]['headers']
            rows = data['resultSets'][0]['rowSet']

            # Índices das colunas que precisamos
            idx_id = headers.index('PERSON_ID')
            idx_name = headers.index('DISPLAY_FIRST_LAST')
            idx_team = headers.index('TEAM_NAME') if 'TEAM_NAME' in headers else None
            idx_team_id = headers.index('TEAM_ID') if 'TEAM_ID' in headers else None

            players = []
            for row in rows:
                nba_id = row[idx_id]
                name = row[idx_name]

                player = {
                    "name": name,
                    "nba_id": nba_id,
                    "photo_url": self.NBA_PHOTO_CDN.format(nba_id=nba_id),
                    "photo_url_small": self.NBA_PHOTO_CDN_260.format(nba_id=nba_id),
                }

                if idx_team is not None:
                    player["team"] = row[idx_team]
                if idx_team_id is not None:
                    player["team_id"] = row[idx_team_id]

                players.append(player)
                self.players_cache[name.lower()] = player

            return players

        except requests.RequestException as e:
            print(f"Erro ao buscar jogadores: {e}")
            return []

    def search_player(self, player_name: str) -> Optional[dict]:
        """
        Busca um jogador específico pelo nome

        Args:
            player_name: Nome do jogador

        Returns:
            Informações do jogador ou None
        """
        # Carrega cache se vazio
        if not self.players_cache:
            self.fetch_all_players()

        name_lower = player_name.lower().strip()

        # Match exato
        if name_lower in self.players_cache:
            return self.players_cache[name_lower]

        # Match parcial com score de similaridade
        best_match = None
        best_score = 0

        for cached_name, player in self.players_cache.items():
            # Similaridade usando SequenceMatcher
            score = SequenceMatcher(None, name_lower, cached_name).ratio()

            # Bonus se contém o nome
            if name_lower in cached_name or cached_name in name_lower:
                score += 0.3

            # Bonus para match de último nome
            search_parts = name_lower.split()
            cached_parts = cached_name.split()
            if len(search_parts) > 1 and len(cached_parts) > 1:
                if search_parts[-1] == cached_parts[-1]:
                    score += 0.2

            if score > best_score and score > 0.6:
                best_score = score
                best_match = player

        return best_match

    def get_photo_url(self, player_name: str, size: str = "large") -> Optional[str]:
        """
        Retorna a URL da foto de um jogador

        Args:
            player_name: Nome do jogador
            size: "large" (1040x760) ou "small" (260x190)

        Returns:
            URL da foto ou None
        """
        player = self.search_player(player_name)
        if player:
            if size == "small":
                return player.get("photo_url_small", player["photo_url"])
            return player["photo_url"]
        return None

    def get_photo_url_by_id(self, nba_id: int, size: str = "large") -> str:
        """
        Gera URL da foto diretamente pelo ID

        Args:
            nba_id: ID do jogador na NBA
            size: "large" ou "small"

        Returns:
            URL da foto
        """
        if size == "small":
            return self.NBA_PHOTO_CDN_260.format(nba_id=nba_id)
        return self.NBA_PHOTO_CDN.format(nba_id=nba_id)


def get_player_photo_url(player_name: str) -> Optional[str]:
    """
    Função utilitária simples para buscar foto de um jogador

    Args:
        player_name: Nome do jogador

    Returns:
        URL da foto ou None
    """
    fetcher = NBAAPIFetcher()
    return fetcher.get_photo_url(player_name)


def get_all_players() -> Dict[str, dict]:
    """
    Retorna dicionário com todos os jogadores

    Returns:
        Dict mapeando nome (lowercase) para informações do jogador
    """
    fetcher = NBAAPIFetcher()
    fetcher.fetch_all_players()
    return fetcher.players_cache


if __name__ == "__main__":
    print("NBA API Fetcher - Teste\n")

    fetcher = NBAAPIFetcher()

    # Busca todos os jogadores
    print("Buscando todos os jogadores da NBA...")
    players = fetcher.fetch_all_players()
    print(f"Encontrados {len(players)} jogadores\n")

    # Testa alguns jogadores
    test_players = [
        "LeBron James",
        "Stephen Curry",
        "Kevin Durant",
        "Giannis Antetokounmpo",
        "Luka Doncic"
    ]

    for name in test_players:
        player = fetcher.search_player(name)
        if player:
            print(f"{player['name']}:")
            print(f"  NBA ID: {player['nba_id']}")
            print(f"  Foto: {player['photo_url']}")
        else:
            print(f"{name}: Não encontrado")
        print()
