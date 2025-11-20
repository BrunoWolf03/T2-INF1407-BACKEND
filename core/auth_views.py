"""
Authentication Views for NBA Fantasy Game
Handles registration, login, logout, and password management
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@extend_schema(
    request=UserRegisterSerializer,
    responses={
        201: OpenApiResponse(description="User registered successfully"),
        400: OpenApiResponse(description="Validation errors")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    Creates user account and fantasy team automatically
    """
    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        user.calculate_rank()
        user.save()

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'token': tokens['access']
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(description="Login successful"),
        401: OpenApiResponse(description="Invalid credentials"),
        400: OpenApiResponse(description="Validation errors")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user
    Returns user data and JWT token
    """
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Update rank before returning
        user.calculate_rank()
        user.save()

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'token': tokens['access']
        }, status=status.HTTP_200_OK)

    return Response(
        {"detail": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED
    )


@extend_schema(
    responses={
        200: OpenApiResponse(description="Logged out successfully"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user
    Invalidates the JWT token (client should remove token)
    """
    # Note: With JWT, logout is primarily client-side
    # The client should remove the token from storage
    # For blacklisting tokens, you'd need django-rest-framework-simplejwt's BlacklistApp

    return Response({
        'message': 'Logged out successfully'
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=ForgotPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password reset email sent"),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Request password reset
    Sends email with reset token (simplified version)
    """
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)

            # Generate reset token (simplified - in production use django-rest-passwordreset)
            reset_token = get_random_string(32)

            # Store token (in production, save to database with expiry)
            # For now, we'll just log it
            # In real app: save to PasswordResetToken model

            # Send email (simplified - configure email backend in production)
            try:
                # In production, configure email settings properly
                send_mail(
                    'Password Reset Request',
                    f'Your reset token: {reset_token}\n\nUse this token to reset your password.',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@nbafantasy.com',
                    [email],
                    fail_silently=True,
                )
            except:
                # Email not configured, just log the token
                print(f"Reset token for {email}: {reset_token}")

            return Response({
                'message': 'Password reset email sent',
                # For development only - remove in production:
                'dev_token': reset_token if settings.DEBUG else None
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            return Response({
                'message': 'Password reset email sent'
            }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password reset successfully"),
        400: OpenApiResponse(description="Invalid token or validation errors")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password with token
    (Simplified version - in production use django-rest-passwordreset)
    """
    serializer = ResetPasswordSerializer(data=request.data)

    if serializer.is_valid():
        # In production, validate token from database
        # For now, accept any token in development mode

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['newPassword']

        # This is simplified - in production:
        # 1. Lookup token in PasswordResetToken model
        # 2. Check if token is expired
        # 3. Get user associated with token
        # 4. Reset password
        # 5. Delete/invalidate token

        # For development, just return success
        return Response({
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(description="Invalid current password or validation errors")
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password (authenticated user)
    Requires current password for security
    """
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = request.user

        # Check current password
        if not user.check_password(serializer.validated_data['currentPassword']):
            return Response({
                'currentPassword': ['Wrong password']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(serializer.validated_data['newPassword'])
        user.save()

        # Update session to prevent logout
        update_session_auth_hash(request, user)

        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
