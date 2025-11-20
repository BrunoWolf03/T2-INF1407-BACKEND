"""
Main Views for NBA Fantasy Game API
Handles players, teams, leaderboard, and dashboard
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from decimal import Decimal
from .models import User, Player, UserTeam, UserTeamPlayer, League
from .serializers import (
    PlayerSerializer,
    UserTeamSerializer,
    UserSerializer,
    UserUpdateSerializer,
    AddPlayerSerializer,
    UpdateFormationSerializer,
    LeaderboardEntrySerializer,
    DashboardStatsSerializer
)


# ===========================
# Player ViewSet
# ===========================

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Player CRUD operations
    List and retrieve NBA players
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter('position', description='Filter by position (PG, SG, SF, PF, C)'),
            OpenApiParameter('team', description='Filter by NBA team'),
            OpenApiParameter('maxPrice', description='Filter by max price'),
            OpenApiParameter('search', description='Search by player name'),
            OpenApiParameter('sortBy', description='Sort by (points, price-high, price-low, name)'),
        ],
        tags=['Players']
    )
    def list(self, request):
        """
        Get all available players with optional filters
        Supports: position, team, maxPrice, search, sortBy
        """
        queryset = self.get_queryset()

        # Filter by position
        position = request.query_params.get('position', None)
        if position:
            queryset = queryset.filter(position_short=position)

        # Filter by team
        team = request.query_params.get('team', None)
        if team:
            queryset = queryset.filter(team__icontains=team)

        # Filter by max price
        max_price = request.query_params.get('maxPrice', None)
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except:
                pass

        # Search by name
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Sort by
        sort_by = request.query_params.get('sortBy', 'points')
        if sort_by == 'points':
            queryset = queryset.order_by('-points')
        elif sort_by == 'price-high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'price-low':
            queryset = queryset.order_by('price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Players'])
    def retrieve(self, request, pk=None):
        """Get single player details"""
        return super().retrieve(request, pk)


# ===========================
# Team Views
# ===========================

@extend_schema(
    responses={200: UserTeamSerializer},
    tags=['Team']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team(request):
    """
    Get current user's team
    Returns team with all players
    """
    try:
        team = UserTeam.objects.get(user=request.user)
        serializer = UserTeamSerializer(team)
        return Response(serializer.data)
    except UserTeam.DoesNotExist:
        # Create team if doesn't exist
        team = UserTeam.objects.create(
            user=request.user,
            name=f"{request.user.username}'s Team"
        )
        serializer = UserTeamSerializer(team)
        return Response(serializer.data)


@extend_schema(
    request=AddPlayerSerializer,
    responses={
        201: OpenApiResponse(description="Player added successfully"),
        400: OpenApiResponse(description="Team is full, insufficient budget, or player not found"),
        404: OpenApiResponse(description="Player not found")
    },
    tags=['Team']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_player_to_team(request):
    """
    Add player to team
    Validates team size (max 5) and budget constraints
    """
    serializer = AddPlayerSerializer(data=request.data)

    if serializer.is_valid():
        player_id = serializer.validated_data['playerId']

        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response(
                {'detail': 'Player not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create user's team
        team, created = UserTeam.objects.get_or_create(
            user=request.user,
            defaults={'name': f"{request.user.username}'s Team"}
        )

        # Check if player can be added
        can_add, message = team.can_add_player(player)
        if not can_add:
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add player to team
        UserTeamPlayer.objects.create(team=team, player=player)

        # Update user's points
        request.user.update_points()
        request.user.calculate_rank()
        request.user.save()

        return Response({
            'message': 'Player added successfully',
            'team': UserTeamSerializer(team).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: OpenApiResponse(description="Player removed successfully"),
        404: OpenApiResponse(description="Player not found in team")
    },
    tags=['Team']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_player_from_team(request, player_id):
    """
    Remove player from team
    """
    try:
        team = UserTeam.objects.get(user=request.user)
    except UserTeam.DoesNotExist:
        return Response(
            {'detail': 'Team not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        team_player = UserTeamPlayer.objects.get(
            team=team,
            player_id=player_id
        )
        team_player.delete()

        # Update user's points
        request.user.update_points()
        request.user.calculate_rank()
        request.user.save()

        return Response({
            'message': 'Player removed successfully',
            'team': UserTeamSerializer(team).data
        }, status=status.HTTP_200_OK)

    except UserTeamPlayer.DoesNotExist:
        return Response(
            {'detail': 'Player not found in team'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    request=UpdateFormationSerializer,
    responses={
        200: OpenApiResponse(description="Formation updated successfully"),
        400: OpenApiResponse(description="Invalid formation")
    },
    tags=['Team']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_formation(request):
    """
    Update team formation
    Options: standard, small-ball, twin-towers
    """
    serializer = UpdateFormationSerializer(data=request.data)

    if serializer.is_valid():
        try:
            team = UserTeam.objects.get(user=request.user)
            team.formation = serializer.validated_data['formation']
            team.save()

            return Response({
                'message': 'Formation updated successfully',
                'team': UserTeamSerializer(team).data
            }, status=status.HTTP_200_OK)

        except UserTeam.DoesNotExist:
            return Response(
                {'detail': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===========================
# User Profile Views
# ===========================

@extend_schema(
    responses={200: UserSerializer},
    tags=['User']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    Get current user profile
    Includes rank, points, and leagues
    """
    # Update rank before returning
    request.user.calculate_rank()
    request.user.save()

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    request=UserUpdateSerializer,
    responses={
        200: OpenApiResponse(description="Profile updated successfully"),
        400: OpenApiResponse(description="Validation errors")
    },
    tags=['User']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile
    Can update username and teamName
    """
    serializer = UserUpdateSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===========================
# Leaderboard
# ===========================

@extend_schema(
    parameters=[
        OpenApiParameter('league', description='Filter by league (global, friends, country)'),
        OpenApiParameter('timeframe', description='Filter by time (overall, month, week)'),
        OpenApiParameter('limit', description='Number of entries (default: 100)'),
    ],
    responses={200: LeaderboardEntrySerializer(many=True)},
    tags=['Leaderboard']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    """
    Get global leaderboard
    Shows top users ranked by total points
    """
    # Get query parameters
    limit = int(request.query_params.get('limit', 100))
    league_filter = request.query_params.get('league', 'global')
    timeframe = request.query_params.get('timeframe', 'overall')

    # Get users ordered by points
    users = User.objects.filter(points__gt=0).order_by('-points')[:limit]

    # Build leaderboard entries
    leaderboard_data = []
    for idx, user in enumerate(users, start=1):
        team_name = "No Team"
        if hasattr(user, 'fantasy_team'):
            team_name = user.fantasy_team.name

        leaderboard_data.append({
            'rank': idx,
            'name': user.username,
            'points': user.points,
            'team': team_name
        })

    serializer = LeaderboardEntrySerializer(leaderboard_data, many=True)
    return Response(serializer.data)


# ===========================
# Dashboard Stats
# ===========================

@extend_schema(
    responses={200: DashboardStatsSerializer},
    tags=['Dashboard']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get user dashboard statistics
    Includes total points, rank, team value, weekly change, and recent activity
    """
    user = request.user

    # Update user stats
    user.update_points()
    user.calculate_rank()
    user.save()

    # Get team
    try:
        team = UserTeam.objects.get(user=user)
        team_value = float(team.total_salary())
        players_count = team.team_players.count()
    except UserTeam.DoesNotExist:
        team_value = 0
        players_count = 0

    # Calculate weekly change (simplified - in production, track historical data)
    weekly_change = 0  # Would need historical data to calculate

    # Get recent activity (simplified)
    recent_activity = []
    # In production, track player performance and show recent games

    stats = {
        'totalPoints': user.points,
        'rank': user.rank,
        'teamValue': team_value,
        'playersCount': players_count,
        'weeklyChange': weekly_change,
        'recentActivity': recent_activity
    }

    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)
