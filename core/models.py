from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # já herda username, email, password
    points = models.IntegerField(default=0) 

# Jogador de NBA
class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, blank=True, null=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    fantasy_points = models.FloatField(default=0)

    def __str__(self):
        return self.name

# Time do usuário (fantasy team)
class FantasyTeam(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="fantasy_team")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    # outros campos que quiser, tipo saldo de orçamento etc.

    def __str__(self):
        return f"{self.name} ({self.user.username})"

# Relação entre time e jogadores
class FantasyTeamPlayer(models.Model):
    team = models.ForeignKey(FantasyTeam, on_delete=models.CASCADE, related_name="players")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "player")  # evita jogador duplicado no mesmo time

    def __str__(self):
        return f"{self.player.name} in {self.team.name}"