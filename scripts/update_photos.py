#!/usr/bin/env python
"""
Script standalone para atualizar fotos dos jogadores no banco Django
Executa fora do management command para uso direto

Uso:
    python scripts/update_photos.py
    python scripts/update_photos.py --dry-run
    python scripts/update_photos.py --player "LeBron James"
"""

import os
import sys
import argparse
import unicodedata

# Configura o Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_fantasy.settings')

import django
django.setup()

# Configura encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests


def safe_print(text):
    """Print seguro que lida com caracteres especiais no Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove acentos e caracteres especiais
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        print(ascii_text)


from difflib import SequenceMatcher
from typing import Optional, Dict
from core.models import Player


class NBAPhotoUpdater:
    """Atualizador de fotos dos jogadores da NBA"""

    NBA_STATS_API = "https://stats.nba.com/stats/commonallplayers"
    NBA_PHOTO_CDN = "https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }

    def __init__(self, dry_run: bool = False, force: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.nba_players: Dict[str, dict] = {}

    def fetch_nba_players(self) -> bool:
        """Busca todos os jogadores da NBA via API"""
        safe_print("[NBA] Buscando jogadores na API da NBA Stats...")

        params = {
            "LeagueID": "00",
            "Season": "2024-25",
            "IsOnlyCurrentSeason": "0"  # Inclui inativos para melhor match
        }

        try:
            session = requests.Session()
            session.headers.update(self.HEADERS)

            response = session.get(self.NBA_STATS_API, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            headers = data['resultSets'][0]['headers']
            rows = data['resultSets'][0]['rowSet']

            idx_id = headers.index('PERSON_ID')
            idx_name = headers.index('DISPLAY_FIRST_LAST')

            for row in rows:
                nba_id = row[idx_id]
                name = row[idx_name]
                key = name.lower().strip()

                self.nba_players[key] = {
                    "name": name,
                    "nba_id": nba_id,
                    "photo_url": self.NBA_PHOTO_CDN.format(nba_id=nba_id)
                }

            safe_print(f"[OK] Encontrados {len(self.nba_players)} jogadores na NBA\n")
            return True

        except requests.RequestException as e:
            safe_print(f"[ERRO] Erro ao buscar jogadores: {e}")
            return False

    def find_match(self, player_name: str) -> Optional[dict]:
        """Encontra o melhor match para um nome"""
        name_lower = player_name.lower().strip()

        # Match exato
        if name_lower in self.nba_players:
            return self.nba_players[name_lower]

        # Match por similaridade
        best_match = None
        best_score = 0

        for key, player in self.nba_players.items():
            score = SequenceMatcher(None, name_lower, key).ratio()

            if name_lower in key or key in name_lower:
                score += 0.3

            search_parts = name_lower.split()
            key_parts = key.split()
            if len(search_parts) > 1 and len(key_parts) > 1:
                if search_parts[-1] == key_parts[-1]:
                    score += 0.2
                if search_parts[0] == key_parts[0]:
                    score += 0.1

            if score > best_score and score > 0.6:
                best_score = score
                best_match = player

        return best_match

    def is_valid_photo(self, url: str) -> bool:
        """Verifica se a URL da foto é válida"""
        if not url:
            return False
        invalid = ['placeholder', 'default', 'via.placeholder']
        return not any(p in url.lower() for p in invalid)

    def update_player(self, player_name: str) -> bool:
        """Atualiza um jogador específico"""
        try:
            player = Player.objects.get(name__icontains=player_name)
        except Player.DoesNotExist:
            safe_print(f"[ERRO] Jogador '{player_name}' nao encontrado no banco")
            return False
        except Player.MultipleObjectsReturned:
            safe_print(f"[AVISO] Multiplos jogadores encontrados para '{player_name}':")
            for p in Player.objects.filter(name__icontains=player_name):
                safe_print(f"   - {p.name}")
            return False

        nba_player = self.find_match(player.name)
        if not nba_player:
            safe_print(f"[ERRO] '{player.name}' nao encontrado na NBA")
            return False

        return self._save_photo(player, nba_player)

    def update_all(self):
        """Atualiza todos os jogadores"""
        players = Player.objects.all()
        total = players.count()

        safe_print(f"[INFO] Processando {total} jogadores do banco...\n")

        updated = 0
        skipped = 0
        not_found = []

        for i, player in enumerate(players, 1):
            # Pula se já tem foto válida
            if not self.force and self.is_valid_photo(player.photo):
                if 'cdn.nba.com' in player.photo:
                    safe_print(f"  [{i}/{total}] {player.name}: [OK] Ja atualizado")
                    skipped += 1
                    continue

            nba_player = self.find_match(player.name)

            if nba_player:
                if self._save_photo(player, nba_player, f"[{i}/{total}]"):
                    updated += 1
                else:
                    skipped += 1
            else:
                safe_print(f"  [{i}/{total}] {player.name}: [X] Nao encontrado")
                not_found.append(player.name)

        # Resumo
        safe_print("\n" + "="*60)
        safe_print(f"[OK] Atualizados: {updated}")
        safe_print(f"[SKIP] Ignorados: {skipped}")
        safe_print(f"[ERRO] Nao encontrados: {len(not_found)}")

        if not_found:
            safe_print("\nJogadores nao encontrados na NBA:")
            for name in not_found:
                safe_print(f"  - {name}")

    def _save_photo(self, player: Player, nba_player: dict, prefix: str = "") -> bool:
        """Salva a foto do jogador"""
        if player.photo == nba_player['photo_url'] and not self.force:
            return False

        safe_print(f"  {prefix} {player.name}:")
        safe_print(f"       -> {nba_player['name']} (ID: {nba_player['nba_id']})")
        safe_print(f"       -> {nba_player['photo_url']}")

        if not self.dry_run:
            player.photo = nba_player['photo_url']
            player.nba_id = nba_player['nba_id']
            player.save(update_fields=['photo', 'nba_id'])
            safe_print("       [OK] Salvo!\n")
        else:
            safe_print("       (dry-run)\n")

        return True


def main():
    parser = argparse.ArgumentParser(description='Atualiza fotos dos jogadores da NBA')
    parser.add_argument('--player', '-p', type=str, help='Nome de um jogador especifico')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Nao salva alteracoes')
    parser.add_argument('--force', '-f', action='store_true', help='Forca atualizacao')

    args = parser.parse_args()

    if args.dry_run:
        safe_print("[AVISO] MODO DRY-RUN: Nenhuma alteracao sera salva\n")

    updater = NBAPhotoUpdater(dry_run=args.dry_run, force=args.force)

    if not updater.fetch_nba_players():
        sys.exit(1)

    if args.player:
        updater.update_player(args.player)
    else:
        updater.update_all()


if __name__ == "__main__":
    main()
