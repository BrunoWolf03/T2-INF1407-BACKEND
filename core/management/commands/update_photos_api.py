"""
Management command para atualizar fotos dos jogadores usando a API da NBA Stats
Alternativa mais rápida ao Selenium
"""

import requests
from typing import Optional, Dict
from difflib import SequenceMatcher

from django.core.management.base import BaseCommand, CommandError
from core.models import Player


class Command(BaseCommand):
    help = 'Atualiza as fotos dos jogadores usando a API da NBA Stats (mais rápido)'

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

    def add_arguments(self, parser):
        parser.add_argument(
            '--player',
            type=str,
            help='Nome de um jogador específico para atualizar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem salvar no banco'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força atualização mesmo se já tiver foto válida'
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Inclui jogadores inativos na busca'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        include_inactive = options['include_inactive']

        if self.dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será salva\n'))

        # Busca jogadores da NBA via API
        self.stdout.write('Buscando jogadores na API da NBA Stats...')
        nba_players = self._fetch_nba_players(not include_inactive)

        if not nba_players:
            raise CommandError('Não foi possível buscar jogadores da API da NBA')

        self.stdout.write(self.style.SUCCESS(f'Encontrados {len(nba_players)} jogadores na NBA\n'))

        # Processa jogadores
        if options['player']:
            self._update_single_player(options['player'], nba_players)
        else:
            self._update_all_players(nba_players)

    def _fetch_nba_players(self, current_only: bool = True) -> Dict[str, dict]:
        """Busca jogadores da API da NBA Stats"""
        params = {
            "LeagueID": "00",
            "Season": "2024-25",
            "IsOnlyCurrentSeason": "1" if current_only else "0"
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

            players = {}
            for row in rows:
                nba_id = row[idx_id]
                name = row[idx_name]
                key = name.lower().strip()

                players[key] = {
                    "name": name,
                    "nba_id": nba_id,
                    "photo_url": self.NBA_PHOTO_CDN.format(nba_id=nba_id)
                }

            return players

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Erro na requisição: {e}'))
            return {}

    def _find_best_match(self, player_name: str, nba_players: Dict[str, dict]) -> Optional[dict]:
        """Encontra o melhor match para um nome de jogador"""
        name_lower = player_name.lower().strip()

        # Match exato
        if name_lower in nba_players:
            return nba_players[name_lower]

        # Match por similaridade
        best_match = None
        best_score = 0

        for key, player in nba_players.items():
            score = SequenceMatcher(None, name_lower, key).ratio()

            # Bonus se um contém o outro
            if name_lower in key or key in name_lower:
                score += 0.3

            # Bonus para match de último nome
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

    def _is_valid_photo(self, photo_url: str) -> bool:
        """Verifica se a foto é válida (não é placeholder)"""
        if not photo_url:
            return False
        invalid = ['placeholder', 'default', 'no-image', 'via.placeholder.com']
        return not any(p in photo_url.lower() for p in invalid)

    def _update_single_player(self, player_name: str, nba_players: Dict[str, dict]):
        """Atualiza um único jogador"""
        try:
            player = Player.objects.get(name__icontains=player_name)
        except Player.DoesNotExist:
            raise CommandError(f'Jogador "{player_name}" não encontrado no banco')
        except Player.MultipleObjectsReturned:
            players = Player.objects.filter(name__icontains=player_name)
            self.stdout.write(self.style.WARNING('Múltiplos jogadores encontrados:'))
            for p in players:
                self.stdout.write(f'  - {p.name}')
            raise CommandError('Seja mais específico')

        nba_player = self._find_best_match(player.name, nba_players)
        if nba_player:
            self._update_player(player, nba_player)
        else:
            self.stdout.write(self.style.WARNING(f'"{player.name}" não encontrado na NBA'))

    def _update_all_players(self, nba_players: Dict[str, dict]):
        """Atualiza todos os jogadores"""
        players = Player.objects.all()
        total = players.count()

        self.stdout.write(f'Processando {total} jogadores do banco...\n')

        updated = 0
        not_found = 0
        skipped = 0
        errors = []

        for i, player in enumerate(players, 1):
            # Pula se já tem foto válida da NBA CDN
            if not self.force and self._is_valid_photo(player.photo):
                if 'cdn.nba.com/headshots' in player.photo:
                    self.stdout.write(f'  [{i}/{total}] {player.name}: ✓ Já atualizado')
                    skipped += 1
                    continue

            nba_player = self._find_best_match(player.name, nba_players)

            if nba_player:
                if self._update_player(player, nba_player, f'[{i}/{total}]'):
                    updated += 1
                else:
                    skipped += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'  [{i}/{total}] {player.name}: ✗ Não encontrado na NBA')
                )
                errors.append(player.name)
                not_found += 1

        # Resumo final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Atualizados: {updated}'))
        self.stdout.write(f'○ Ignorados (já atualizados): {skipped}')
        self.stdout.write(self.style.WARNING(f'✗ Não encontrados: {not_found}'))

        if errors:
            self.stdout.write('\nJogadores não encontrados:')
            for name in errors:
                self.stdout.write(f'  - {name}')

    def _update_player(self, player: Player, nba_player: dict, prefix: str = '') -> bool:
        """Atualiza foto de um jogador"""
        old_photo = player.photo
        new_photo = nba_player['photo_url']
        nba_id = nba_player['nba_id']

        if old_photo == new_photo and not self.force:
            return False

        self.stdout.write(
            f'  {prefix} {player.name}:\n'
            f'       Match: {nba_player["name"]} (ID: {nba_id})\n'
            f'       Foto: {new_photo}'
        )

        if not self.dry_run:
            player.photo = new_photo
            player.nba_id = nba_id
            player.save(update_fields=['photo', 'nba_id'])
            self.stdout.write(self.style.SUCCESS('       → Salvo!\n'))
        else:
            self.stdout.write(self.style.WARNING('       → (dry-run)\n'))

        return True
