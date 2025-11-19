from rest_framework import routers
from django.urls import path, include
from .views import UserViewSet, PlayerViewSet, FantasyTeamViewSet, FantasyTeamPlayerViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'fantasy-teams', FantasyTeamViewSet)
router.register(r'fantasy-team-players', FantasyTeamPlayerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
