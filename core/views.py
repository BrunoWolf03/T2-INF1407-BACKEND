from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Player, FantasyTeam, FantasyTeamPlayer
from .serializers import UserSerializer, PlayerSerializer, FantasyTeamSerializer, FantasyTeamPlayerSerializer

# -------------------------
# Usuários
# -------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # só usuários autenticados podem acessar

# -------------------------
# Jogadores
# -------------------------
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

# -------------------------
# Times Fantasy
# -------------------------
class FantasyTeamViewSet(viewsets.ModelViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [IsAuthenticated]

# -------------------------
# Jogadores no Time
# -------------------------
class FantasyTeamPlayerViewSet(viewsets.ModelViewSet):
    queryset = FantasyTeamPlayer.objects.all()
    serializer_class = FantasyTeamPlayerSerializer
    permission_classes = [IsAuthenticated]
