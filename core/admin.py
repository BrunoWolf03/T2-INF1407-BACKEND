"""
Django Admin configuration for NBA Fantasy Game
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Player, UserTeam, UserTeamPlayer, League, LeagueMembership


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ('username', 'email', 'team_name', 'points', 'rank', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'team_name')
    ordering = ('-points',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Fantasy Info', {'fields': ('team_name', 'points', 'rank')}),
    )


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Admin interface for Player model"""
    list_display = ('name', 'position_short', 'team', 'price', 'points', 'stats_points')
    list_filter = ('position_short', 'team')
    search_fields = ('name', 'team')
    ordering = ('-points',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'position', 'position_short', 'team', 'photo')
        }),
        ('Fantasy Data', {
            'fields': ('price', 'points')
        }),
        ('Statistics', {
            'fields': ('stats_points', 'stats_rebounds', 'stats_assists', 'stats_steals', 'stats_blocks')
        }),
    )


@admin.register(UserTeam)
class UserTeamAdmin(admin.ModelAdmin):
    """Admin interface for UserTeam model"""
    list_display = ('name', 'user', 'budget', 'formation', 'player_count', 'total_points')
    list_filter = ('formation',)
    search_fields = ('name', 'user__username')
    ordering = ('-created_at',)

    def player_count(self, obj):
        """Display number of players in team"""
        return obj.team_players.count()
    player_count.short_description = 'Players'

    def total_points(self, obj):
        """Display total fantasy points"""
        return obj.total_points()
    total_points.short_description = 'Total Points'


@admin.register(UserTeamPlayer)
class UserTeamPlayerAdmin(admin.ModelAdmin):
    """Admin interface for UserTeamPlayer model"""
    list_display = ('player', 'team', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('player__name', 'team__name')
    ordering = ('-added_at',)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin interface for League model"""
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(LeagueMembership)
class LeagueMembershipAdmin(admin.ModelAdmin):
    """Admin interface for LeagueMembership model"""
    list_display = ('user', 'league', 'rank', 'joined_at')
    list_filter = ('league',)
    search_fields = ('user__username', 'league__name')
    ordering = ('league', 'rank')
