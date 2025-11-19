import requests
from django.core.management.base import BaseCommand
from core.models import Player

class Command(BaseCommand):
    help = 'Importa jogadores da NBA usando a API balldontlie'

    def handle(self, *args, **kwargs):
        self.stdout.write("Importando jogadores da NBA...")

        page = 1
        per_page = 100
        url_base = "https://www.balldontlie.io/api/v1/players"

        while True:
            url = f"{url_base}?per_page={per_page}&page={page}"
            response = requests.get(url)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Erro na API: {response.status_code}"))
                break

            try:
                data = response.json()
            except ValueError:
                self.stdout.write(self.style.ERROR("Resposta da API não é um JSON válido"))
                break

            players = data.get('data', [])
            if not players:
                break  # não há mais jogadores

            for p in players:
                Player.objects.update_or_create(
                    name=f"{p['first_name']} {p['last_name']}",
                    defaults={
                        'position': p['position'] or '',
                        'team_name': p['team']['full_name'] if p['team'] else '',
                        'fantasy_points': 0
                    }
                )

            # Próxima página
            if data['meta']['next_page']:
                page += 1
            else:
                break

        self.stdout.write(self.style.SUCCESS("Importação finalizada!"))
