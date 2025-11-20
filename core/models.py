"""
Models for NBA Fantasy Game
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Includes fantasy-specific fields
    """
    team_name = models.CharField(max_length=50, blank=True, default="")
    points = models.IntegerField(default=0, help_text="Total fantasy points")
    rank = models.IntegerField(default=0, help_text="Global ranking position")

    def __str__(self):
        return self.username

    def calculate_rank(self):
        """Calculate user's global rank based on points"""
        # Count how many users have more points
        higher_ranked = User.objects.filter(points__gt=self.points).count()
        self.rank = higher_ranked + 1
        return self.rank

    def update_points(self):
        """Update total points from user's fantasy team"""
        if hasattr(self, 'fantasy_team'):
            total = sum(
                player.player.points
                for player in self.fantasy_team.team_players.all()
            )
            self.points = total
            self.save()


class Player(models.Model):
    """
    NBA Player model with stats and pricing
    """
    POSITION_CHOICES = [
        ('PG', 'Point Guard'),
        ('SG', 'Shooting Guard'),
        ('SF', 'Small Forward'),
        ('PF', 'Power Forward'),
        ('C', 'Center'),
    ]

    # Basic info
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, help_text="Full position name")
    position_short = models.CharField(
        max_length=2,
        choices=POSITION_CHOICES,
        help_text="Short position code"
    )
    team = models.CharField(max_length=100, help_text="NBA team name")

    # Fantasy data
    price = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.1'))],
        help_text="Salary in millions"
    )
    points = models.IntegerField(default=0, help_text="Total fantasy points")
    photo = models.URLField(
        blank=True,
        default="https://via.placeholder.com/150",
        help_text="URL to player photo"
    )

    # Stats (per game averages)
    stats_points = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Points per game"
    )
    stats_rebounds = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Rebounds per game"
    )
    stats_assists = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Assists per game"
    )
    stats_steals = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Steals per game"
    )
    stats_blocks = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Blocks per game"
    )

    class Meta:
        ordering = ['-points', 'name']

    def __str__(self):
        return f"{self.name} ({self.position_short})"


class UserTeam(models.Model):
    """
    User's Fantasy Team
    Each user has one team with up to 5 players
    """
    FORMATION_CHOICES = [
        ('standard', 'Standard'),
        ('small-ball', 'Small Ball'),
        ('twin-towers', 'Twin Towers'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="fantasy_team"
    )
    name = models.CharField(max_length=50)
    budget = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('200.0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Total salary cap in millions"
    )
    formation = models.CharField(
        max_length=20,
        choices=FORMATION_CHOICES,
        default='standard'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def total_salary(self):
        """Calculate total salary of all players in team"""
        return sum(
            player.player.price
            for player in self.team_players.all()
        )

    def remaining_budget(self):
        """Calculate remaining budget"""
        return float(self.budget) - float(self.total_salary())

    def can_add_player(self, player):
        """
        Check if a player can be added to the team
        Returns (bool, str) - (can_add, error_message)
        """
        # Check team size
        if self.team_players.count() >= 5:
            return False, "Team is full (max 5 players)"

        # Check if player already in team
        if self.team_players.filter(player=player).exists():
            return False, "Player already in team"

        # Check budget
        if self.total_salary() + player.price > self.budget:
            return False, "Insufficient budget"

        return True, "OK"

    def total_points(self):
        """Calculate total fantasy points of team"""
        return sum(
            player.player.points
            for player in self.team_players.all()
        )


class UserTeamPlayer(models.Model):
    """
    Many-to-Many relationship between UserTeam and Player
    Tracks which players are in which teams
    """
    team = models.ForeignKey(
        UserTeam,
        on_delete=models.CASCADE,
        related_name="team_players"
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="in_teams"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "player")
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.player.name} in {self.team.name}"


class League(models.Model):
    """
    League model for private leagues (optional feature)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_leagues"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class LeagueMembership(models.Model):
    """
    Many-to-Many relationship between User and League
    Tracks user rankings within specific leagues
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "league")
        ordering = ['rank', '-user__points']

    def __str__(self):
        return f"{self.user.username} in {self.league.name}"
