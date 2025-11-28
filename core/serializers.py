"""
Serializers for NBA Fantasy Game API
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, Player, UserTeam, UserTeamPlayer, League, LeagueMembership


# ===========================
# Player Serializers
# ===========================

class PlayerStatsSerializer(serializers.Serializer):
    """Nested serializer for player stats"""
    points = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        source='stats_points'
    )
    rebounds = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        source='stats_rebounds'
    )
    assists = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        source='stats_assists'
    )
    steals = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        source='stats_steals'
    )
    blocks = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        source='stats_blocks'
    )


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model"""
    stats = PlayerStatsSerializer(source='*', read_only=True)
    positionShort = serializers.CharField(source='position_short')

    class Meta:
        model = Player
        fields = [
            'id',
            'name',
            'position',
            'positionShort',
            'team',
            'price',
            'points',
            'photo',
            'stats'
        ]


# ===========================
# User/Auth Serializers
# ===========================

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirmPassword = serializers.CharField(write_only=True, required=True)
    teamName = serializers.CharField(source='team_name', required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'confirmPassword',
            'teamName'
        ]

    def validate(self, attrs):
        """Validate unique amail"""
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "Email já está registrado."
            })
        
        """Validate that passwords match"""
        if attrs['password'] != attrs.pop('confirmPassword'):
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        """Create new user with encrypted password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            team_name=validated_data.get('team_name', '')
        )
        # Create fantasy team for user
        UserTeam.objects.create(
            user=user,
            name=validated_data.get('team_name', f"{user.username}'s Team")
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    rememberMe = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        """Validate credentials"""
        email = attrs.get('email')
        password = attrs.get('password')

        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Authenticate user
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs['user'] = user
        return attrs


class LeagueBasicSerializer(serializers.ModelSerializer):
    """Basic league info for nested serialization"""
    class Meta:
        model = League
        fields = ['id', 'name']


class LeagueWithRankSerializer(serializers.Serializer):
    """League with user's rank"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    rank = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    teamName = serializers.CharField(source='team_name')
    leagues = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'teamName',
            'rank',
            'points',
            'leagues'
        ]

    def get_leagues(self, obj):
        """Get user's leagues with ranks"""
        memberships = LeagueMembership.objects.filter(user=obj).select_related('league')
        return [
            {
                'id': m.league.id,
                'name': m.league.name,
                'rank': m.rank
            }
            for m in memberships
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    teamName = serializers.CharField(source='team_name', required=False)

    class Meta:
        model = User
        fields = ['username', 'teamName']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    currentPassword = serializers.CharField(required=True, write_only=True)
    newPassword = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    confirmPassword = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate passwords"""
        if attrs['newPassword'] != attrs['confirmPassword']:
            raise serializers.ValidationError({
                "newPassword": "Password fields didn't match."
            })
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password"""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for reset password"""
    token = serializers.CharField(required=True)
    newPassword = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    confirmPassword = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate passwords"""
        if attrs['newPassword'] != attrs['confirmPassword']:
            raise serializers.ValidationError({
                "newPassword": "Password fields didn't match."
            })
        return attrs


# ===========================
# Team Serializers
# ===========================

class UserTeamPlayerSerializer(serializers.ModelSerializer):
    """Serializer for players in a user's team"""
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = UserTeamPlayer
        fields = ['id', 'player', 'added_at']


class UserTeamSerializer(serializers.ModelSerializer):
    """Serializer for UserTeam model"""
    userId = serializers.IntegerField(source='user.id', read_only=True)
    players = serializers.SerializerMethodField()

    class Meta:
        model = UserTeam
        fields = [
            'id',
            'userId',
            'name',
            'budget',
            'formation',
            'players'
        ]

    def get_players(self, obj):
        """Get all players in the team"""
        team_players = obj.team_players.select_related('player').all()
        return [
            PlayerSerializer(tp.player).data
            for tp in team_players
        ]


class AddPlayerSerializer(serializers.Serializer):
    """Serializer for adding player to team"""
    playerId = serializers.IntegerField(required=True)

    def validate_playerId(self, value):
        """Validate that player exists"""
        try:
            Player.objects.get(id=value)
        except Player.DoesNotExist:
            raise serializers.ValidationError("Player not found")
        return value


class UpdateFormationSerializer(serializers.Serializer):
    """Serializer for updating team formation"""
    formation = serializers.ChoiceField(
        choices=UserTeam.FORMATION_CHOICES,
        required=True
    )


# ===========================
# Leaderboard Serializers
# ===========================

class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entries"""
    rank = serializers.IntegerField()
    name = serializers.CharField()
    points = serializers.IntegerField()
    team = serializers.CharField()


# ===========================
# Dashboard Serializers
# ===========================

class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent player activity"""
    playerId = serializers.IntegerField()
    playerName = serializers.CharField()
    action = serializers.CharField()
    value = serializers.IntegerField()
    points = serializers.IntegerField()
    timestamp = serializers.DateTimeField()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    totalPoints = serializers.IntegerField()
    rank = serializers.IntegerField()
    teamValue = serializers.DecimalField(max_digits=5, decimal_places=1)
    playersCount = serializers.IntegerField()
    weeklyChange = serializers.IntegerField()
    recentActivity = RecentActivitySerializer(many=True)


# ===========================
# League Serializers
# ===========================

class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for League model"""
    createdBy = serializers.StringRelatedField(source='created_by')

    class Meta:
        model = League
        fields = ['id', 'name', 'description', 'createdBy', 'created_at']


class LeagueMembershipSerializer(serializers.ModelSerializer):
    """Serializer for League Membership"""
    user = UserSerializer(read_only=True)
    league = LeagueSerializer(read_only=True)

    class Meta:
        model = LeagueMembership
        fields = ['id', 'user', 'league', 'rank', 'joined_at']
