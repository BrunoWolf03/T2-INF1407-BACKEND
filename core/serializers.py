from rest_framework import serializers
from .models import User, Player, FantasyTeam, FantasyTeamPlayer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'points', 'is_staff']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'team_name', 'fantasy_points']

class FantasyTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyTeam
        fields = ['id', 'name', 'user', 'created_at']

class FantasyTeamPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    player_id = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), source='player', write_only=True)

    class Meta:
        model = FantasyTeamPlayer
        fields = ['id', 'team', 'player', 'player_id', 'added_at']
