from django.contrib import admin
from .models import User

# Registra apenas o User (se você quiser)
admin.site.register(User)
