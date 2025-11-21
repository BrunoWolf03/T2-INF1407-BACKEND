"""
NBA Player Photo Scraper
Busca fotos de jogadores no site oficial da NBA usando web scraping
"""

import time
import re
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class NBAPhotoScraper:
    """Scraper para buscar fotos de jogadores da NBA"""

    NBA_PLAYERS_URL = "https://www.nba.com/players"
    NBA_PHOTO_CDN = "https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_id}.png"

    def __init__(self, headless: bool = True):
        """
        Inicializa o scraper

        Args:
            headless: Se True, executa o browser sem interface gráfica
        """
        self.headless = headless
        self.driver = None
        self.players_cache: Dict[str, dict] = {}

    def _setup_driver(self):
        """Configura o Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)

    def _close_driver(self):
        """Fecha o WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def load_all_players(self) -> List[dict]:
        """
        Carrega todos os jogadores da página da NBA

        Returns:
            Lista de dicionários com informações dos jogadores
        """
        try:
            self._setup_driver()
            self.driver.get(self.NBA_PLAYERS_URL)

            # Espera a página carregar
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.players-list"))
            )

            # Scroll para carregar todos os jogadores (lazy loading)
            self._scroll_to_load_all()

            # Busca todos os links de jogadores
            players = []
            player_links = self.driver.find_elements(By.CSS_SELECTOR, "a.RosterRow_playerLink__qw1vG")

            for link in player_links:
                try:
                    href = link.get_attribute("href")
                    name = link.text.strip()

                    # Extrai o nba_id da URL (ex: /player/1629638/trae-young)
                    match = re.search(r'/player/(\d+)/', href)
                    if match:
                        nba_id = int(match.group(1))
                        player_info = {
                            "name": name,
                            "nba_id": nba_id,
                            "photo_url": self.NBA_PHOTO_CDN.format(nba_id=nba_id),
                            "profile_url": href
                        }
                        players.append(player_info)
                        self.players_cache[name.lower()] = player_info
                except Exception as e:
                    print(f"Erro ao processar jogador: {e}")
                    continue

            return players

        finally:
            self._close_driver()

    def _scroll_to_load_all(self):
        """Faz scroll na página para carregar todos os jogadores"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll até o final
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

            # Calcula nova altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def search_player_by_name(self, player_name: str) -> Optional[dict]:
        """
        Busca um jogador específico pelo nome

        Args:
            player_name: Nome do jogador (ex: "LeBron James")

        Returns:
            Dicionário com informações do jogador ou None se não encontrado
        """
        # Verifica cache primeiro
        name_lower = player_name.lower()
        if name_lower in self.players_cache:
            return self.players_cache[name_lower]

        try:
            self._setup_driver()
            self.driver.get(self.NBA_PLAYERS_URL)

            # Espera a página carregar
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search Players']"))
            )

            # Busca o campo de pesquisa e digita o nome
            search_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search Players']")
            search_input.clear()
            search_input.send_keys(player_name)

            time.sleep(2)  # Aguarda filtrar

            # Busca o jogador nos resultados
            player_links = self.driver.find_elements(By.CSS_SELECTOR, "a.RosterRow_playerLink__qw1vG")

            for link in player_links:
                try:
                    href = link.get_attribute("href")
                    name = link.text.strip()

                    # Verifica se o nome corresponde (busca flexível)
                    if self._names_match(player_name, name):
                        match = re.search(r'/player/(\d+)/', href)
                        if match:
                            nba_id = int(match.group(1))
                            player_info = {
                                "name": name,
                                "nba_id": nba_id,
                                "photo_url": self.NBA_PHOTO_CDN.format(nba_id=nba_id),
                                "profile_url": href
                            }
                            self.players_cache[name.lower()] = player_info
                            return player_info
                except Exception:
                    continue

            return None

        except TimeoutException:
            print(f"Timeout ao buscar jogador: {player_name}")
            return None
        finally:
            self._close_driver()

    def get_player_photo_from_profile(self, player_name: str) -> Optional[str]:
        """
        Busca a foto de um jogador acessando sua página de perfil

        Args:
            player_name: Nome do jogador

        Returns:
            URL da foto ou None
        """
        try:
            self._setup_driver()

            # Primeiro busca o jogador na lista
            player_info = self.search_player_by_name(player_name)
            if not player_info:
                return None

            # Acessa a página do perfil
            self.driver.get(player_info["profile_url"])

            # Espera a imagem carregar
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.PlayerImage_image__wH_YX"))
            )

            # Busca a imagem
            img = self.driver.find_element(By.CSS_SELECTOR, "img.PlayerImage_image__wH_YX")
            photo_url = img.get_attribute("src")

            return photo_url

        except Exception as e:
            print(f"Erro ao buscar foto do perfil: {e}")
            # Fallback: usa a URL do CDN se tiver o nba_id
            if player_info and player_info.get("nba_id"):
                return player_info["photo_url"]
            return None
        finally:
            self._close_driver()

    def _names_match(self, search_name: str, found_name: str) -> bool:
        """
        Verifica se dois nomes correspondem (busca flexível)

        Args:
            search_name: Nome buscado
            found_name: Nome encontrado

        Returns:
            True se os nomes correspondem
        """
        search_lower = search_name.lower().strip()
        found_lower = found_name.lower().strip()

        # Match exato
        if search_lower == found_lower:
            return True

        # Match parcial (nome contém a busca)
        if search_lower in found_lower or found_lower in search_lower:
            return True

        # Match por partes do nome
        search_parts = search_lower.split()
        found_parts = found_lower.split()

        # Se o último nome e primeiro nome batem
        if len(search_parts) >= 2 and len(found_parts) >= 2:
            if search_parts[0] == found_parts[0] and search_parts[-1] == found_parts[-1]:
                return True

        return False

    def get_photo_url_by_nba_id(self, nba_id: int) -> str:
        """
        Gera a URL da foto diretamente pelo nba_id

        Args:
            nba_id: ID oficial do jogador na NBA

        Returns:
            URL da foto no CDN da NBA
        """
        return self.NBA_PHOTO_CDN.format(nba_id=nba_id)


# Função utilitária para uso simples
def get_player_photo(player_name: str, headless: bool = True) -> Optional[str]:
    """
    Busca a foto de um jogador pelo nome

    Args:
        player_name: Nome do jogador
        headless: Se True, executa sem interface gráfica

    Returns:
        URL da foto ou None
    """
    scraper = NBAPhotoScraper(headless=headless)
    player_info = scraper.search_player_by_name(player_name)
    if player_info:
        return player_info["photo_url"]
    return None


if __name__ == "__main__":
    # Exemplo de uso
    scraper = NBAPhotoScraper(headless=True)

    # Buscar um jogador específico
    print("Buscando LeBron James...")
    player = scraper.search_player_by_name("LeBron James")
    if player:
        print(f"Nome: {player['name']}")
        print(f"NBA ID: {player['nba_id']}")
        print(f"Foto: {player['photo_url']}")
    else:
        print("Jogador não encontrado")

    print("\n" + "="*50 + "\n")

    # Buscar outro jogador
    print("Buscando Stephen Curry...")
    player = scraper.search_player_by_name("Stephen Curry")
    if player:
        print(f"Nome: {player['name']}")
        print(f"NBA ID: {player['nba_id']}")
        print(f"Foto: {player['photo_url']}")
