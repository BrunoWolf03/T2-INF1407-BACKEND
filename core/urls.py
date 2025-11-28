"""
URL Configuration for NBA Fantasy Game API
Maps URLs to views
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, auth_views

# Create router for viewsets
router = DefaultRouter()
router.register(r'players', views.PlayerViewSet, basename='player')

urlpatterns = [
    # ===========================
    # Authentication Endpoints
    # ===========================
    path('auth/register', auth_views.register, name='auth-register'),
    path('auth/login', auth_views.login, name='auth-login'),
    path('auth/logout', auth_views.logout, name='auth-logout'),
    path('auth/forgot-password', auth_views.forgot_password, name='auth-forgot-password'),
    path('auth/reset-password', auth_views.reset_password, name='auth-reset-password'),
    path('auth/change-password', auth_views.change_password, name='auth-change-password'),

    # ===========================
    # Team Endpoints
    # ===========================
    path('team', views.get_team, name='team-get'),
    path('team/players', views.add_player_to_team, name='team-add-player'),
    path('team/players/<int:player_id>', views.remove_player_from_team, name='team-remove-player'),
    path('team/formation', views.update_formation, name='team-update-formation'),

    # ===========================
    # User Profile Endpoints
    # ===========================
    path('user/profile', views.get_profile, name='user-profile-get'),
    path('user/profile/update', views.update_profile, name='user-profile-update'),

    # ===========================
    # Leaderboard
    # ===========================
    path('leaderboard', views.leaderboard, name='leaderboard'),

    # ===========================
    # Dashboard
    # ===========================
    path('dashboard/stats', views.dashboard_stats, name='dashboard-stats'),

    # ===========================
    # Admin Endpoints
    # ===========================
    path('admin/fetch-players', views.fetch_balldontlie_api, name='admin-fetch-players'),

]
