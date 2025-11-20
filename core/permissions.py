"""
Custom Permissions for NBA Fantasy Game API
"""
from rest_framework.permissions import BasePermission


class IsAdminOrSuperuser(BasePermission):
    """
    Permission class that allows access to users who are either:
    - Staff members (is_staff=True)
    - Superusers (is_superuser=True)

    This is more flexible than DRF's default IsAdminUser which only checks is_staff.
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated and has admin privileges
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )
