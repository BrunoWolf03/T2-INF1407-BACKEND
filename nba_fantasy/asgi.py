import os
from django.core.asgi import get_asgi_application

# Define o settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nba_fantasy.settings")

# Cria a aplicação ASGI
application = get_asgi_application()
