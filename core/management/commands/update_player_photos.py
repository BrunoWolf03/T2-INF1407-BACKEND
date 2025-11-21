"""
Management command para atualizar fotos dos jogadores da NBA
Usa web scraping no site oficial da NBA
"""

import sys
import os
import time
import re
from typing import Optional, Dict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Adiciona o diretório scripts ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from core.models import Player

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class Command(BaseCommand):
    help = 'Atualiza as fotos dos jogadores buscando no site oficial da NBA'

    NBA_PLAYERS_URL = "https://www.nba.com/players"
    NBA_PHOTO_CDN = "https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png"

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
            '--no-headless',
            action='store_true',
            help='Executa o browser com interface gráfica (para debug)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força atualização mesmo se já tiver foto válida'
        )

    def handle(self, *args, **options):
        if not SELENIUM_AVAILABLE:
            raise CommandError(
                'Selenium não está instalado. Execute: pip install selenium\n'
                'Você também precisa do ChromeDriver instalado.'
            )

        self.dry_run = options['dry_run']
        self.headless = not options['no_headless']
        self.force = options['force']

        if self.dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será salva'))

        # Busca jogadores da NBA
        self.stdout.write('Buscando jogadores no site da NBA...')
        nba_players = self._fetch_nba_players()

        if not nba_players:
            raise CommandError('Não foi possível buscar jogadores da NBA')

        self.stdout.write(self.style.SUCCESS(f'Encontrados {len(nba_players)} jogadores na NBA'))

        # Filtra jogadores se especificado
        if options['player']:
            self._update_single_player(options['player'], nba_players)
        else:
            self._update_all_players(nba_players)

    def _setup_driver(self):
        """Configura o Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        return webdriver.Chrome(options=chrome_options)

    def _fetch_nba_players(self) -> Dict[str, dict]:
        """Busca todos os jogadores da página da NBA"""
        driver = None
        try:
            driver = self._setup_driver()
            driver.get(self.NBA_PLAYERS_URL)

            # Espera a tabela carregar
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.players-list"))
            )

            # Scroll para carregar todos os jogadores
            self._scroll_to_load_all(driver)

            # Busca todos os links de jogadores
            players = {}
            player_links = driver.find_elements(By.CSS_SELECTOR, "a.RosterRow_playerLink__qw1vG")

            for link in player_links:
                try:
                    href = link.get_attribute("href")
                    name = link.text.strip()

                    # Extrai o nba_id da URL
                    match = re.search(r'/player/(\d+)/', href)
                    if match:
                        nba_id = int(match.group(1))
                        # Usa nome em lowercase como chave para facilitar busca
                        key = self._normalize_name(name)
                        players[key] = {
                            "name": name,
                            "nba_id": nba_id,
                            "photo_url": self.NBA_PHOTO_CDN.format(nba_id=nba_id)
                        }
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Erro ao processar jogador: {e}'))
                    continue

            return players

        except TimeoutException:
            self.stdout.write(self.style.ERROR('Timeout ao carregar página da NBA'))
            return {}
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao buscar jogadores: {e}'))
            return {}
        finally:
            if driver:
                driver.quit()

    def _scroll_to_load_all(self, driver):
        """Faz scroll na página para carregar todos os jogadores (lazy loading)"""
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _normalize_name(self, name: str) -> str:
        """Normaliza nome para comparação"""
        # Remove acentos e caracteres especiais, converte para lowercase
        name = name.lower().strip()
        # Remove Jr., Sr., III, etc.
        name = re.sub(r'\s+(jr\.?|sr\.?|iii|ii|iv)$', '', name, flags=re.IGNORECASE)
        return name

    def _find_best_match(self, player_name: str, nba_players: Dict[str, dict]) -> Optional[dict]:
        """Encontra o melhor match para um jogador"""
        normalized = self._normalize_name(player_name)

        # Match exato
        if normalized in nba_players:
            return nba_players[normalized]

        # Match parcial
        for key, player in nba_players.items():
            # Nome contém a busca ou vice-versa
            if normalized in key or key in normalized:
                return player

            # Match por primeiro e último nome
            search_parts = normalized.split()
            key_parts = key.split()

            if len(search_parts) >= 2 and len(key_parts) >= 2:
                if search_parts[0] == key_parts[0] and search_parts[-1] == key_parts[-1]:
                    return player

                # Match por último nome apenas (pode ser ambíguo)
                if search_parts[-1] == key_parts[-1]:
                    # Verifica se primeiro nome é similar
                    if search_parts[0][:3] == key_parts[0][:3]:
                        return player

        return None

    def _is_valid_photo(self, photo_url: str) -> bool:
        """Verifica se a URL da foto é válida (não é placeholder)"""
        if not photo_url:
            return False
        invalid_patterns = [
            'placeholder',
            'default',
            'no-image',
            'via.placeholder.com'
        ]
        return not any(pattern in photo_url.lower() for pattern in invalid_patterns)

    def _update_single_player(self, player_name: str, nba_players: Dict[str, dict]):
        """Atualiza foto de um único jogador"""
        try:
            player = Player.objects.get(name__icontains=player_name)
        except Player.DoesNotExist:
            raise CommandError(f'Jogador "{player_name}" não encontrado no banco')
        except Player.MultipleObjectsReturned:
            players = Player.objects.filter(name__icontains=player_name)
            self.stdout.write(self.style.WARNING(f'Múltiplos jogadores encontrados:'))
            for p in players:
                self.stdout.write(f'  - {p.name}')
            raise CommandError('Seja mais específico no nome do jogador')

        nba_player = self._find_best_match(player.name, nba_players)

        if nba_player:
            self._update_player_photo(player, nba_player)
        else:
            self.stdout.write(self.style.WARNING(f'Jogador "{player.name}" não encontrado na NBA'))

    def _update_all_players(self, nba_players: Dict[str, dict]):
        """Atualiza fotos de todos os jogadores no banco"""
        players = Player.objects.all()
        total = players.count()

        self.stdout.write(f'\nAtualizando {total} jogadores do banco...\n')

        updated = 0
        not_found = 0
        skipped = 0

        for player in players:
            # Verifica se precisa atualizar
            if not self.force and self._is_valid_photo(player.photo):
                if player.photo.startswith('https://cdn.nba.com/headshots'):
                    self.stdout.write(f'  [{skipped + updated + not_found + 1}/{total}] {player.name}: Foto já atualizada (skip)')
                    skipped += 1
                    continue

            nba_player = self._find_best_match(player.name, nba_players)

            if nba_player:
                if self._update_player_photo(player, nba_player):
                    updated += 1
                else:
                    skipped += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'  [{skipped + updated + not_found + 1}/{total}] {player.name}: Não encontrado na NBA')
                )
                not_found += 1

        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Atualizados: {updated}'))
        self.stdout.write(self.style.WARNING(f'Não encontrados: {not_found}'))
        self.stdout.write(f'Ignorados (já atualizados): {skipped}')

    def _update_player_photo(self, player: Player, nba_player: dict) -> bool:
        """Atualiza a foto de um jogador"""
        old_photo = player.photo
        new_photo = nba_player['photo_url']
        nba_id = nba_player['nba_id']

        if old_photo == new_photo and not self.force:
            self.stdout.write(f'  {player.name}: Foto já está atualizada')
            return False

        self.stdout.write(
            f'  {player.name}:\n'
            f'    NBA ID: {nba_id}\n'
            f'    Foto antiga: {old_photo}\n'
            f'    Foto nova: {new_photo}'
        )

        if not self.dry_run:
            player.photo = new_photo
            player.nba_id = nba_id
            player.save(update_fields=['photo', 'nba_id'])
            self.stdout.write(self.style.SUCCESS(f'    ✓ Atualizado!'))

        return True


# Função auxiliar para ser chamada diretamente (sem management command)
def update_all_photos(dry_run: bool = False, force: bool = False):
    """
    Função auxiliar para atualizar todas as fotos programaticamente

    Args:
        dry_run: Se True, não salva alterações
        force: Se True, atualiza mesmo fotos já válidas
    """
    from django.core.management import call_command
    args = []
    if dry_run:
        args.append('--dry-run')
    if force:
        args.append('--force')
    call_command('update_player_photos', *args)
