web: gunicorn nba_fantasy.wsgi --log-file -
release: python manage.py migrate && python manage.py loaddata players
