import requests

class BallDontLieService:

    BASE_URL = "https://www.balldontlie.io/api/v1/players"  # v1 NÃO precisa de chave

    @staticmethod
    def get_players(page=1, per_page=100):

        params = {
            "page": page,
            "per_page": per_page
        }

        response = requests.get(
            BallDontLieService.BASE_URL,
            params=params
        )

        if response.status_code != 200:
            print("Erro ao chamar balldontlie:", response.status_code, response.text)
            return None

        return response.json()
