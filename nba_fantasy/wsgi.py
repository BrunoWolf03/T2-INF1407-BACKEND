import os
from django.core.wsgi import get_wsgi_application

# Define o settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nba_fantasy.settings")

# Cria a aplicação WSGI
application = get_wsgi_application()
