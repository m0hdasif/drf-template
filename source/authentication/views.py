import logging

from rest_framework import generics, mixins, serializers, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.models import User
from authentication.permissions import IsOwnProfile
from authentication.serializers import (
    ChangePasswordSerializer,
    RegistrationSerializer,
    TokenObtainLifetimeSerializer,
    TokenRefreshLifetimeSerializer,
    UserActivationSerializer,
    UserProfileSerializer,
    UserSerializer,
    UserStatusSerializer,
)

from . import signals

logger = logging.getLogger(__name__)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Log out successfully"}, status=status.HTTP_200_OK)


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "activation":
            return UserActivationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ["update", "create", "retrieve", "me", "update_status"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["reset_password"]:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):

        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        return user

    def perform_update(self, serializer):
        return serializer.save()

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(instance=self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"])
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserStatusSerializer(instance, request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"data": serializer.data, "message": "user status updated successfully"}
        )

    @action(detail=True, methods=["PUT"])
    def reset_password(self, request, *args, **kwargs):
        instance = self.get_object()
        new_password = request.data.get("new_password")
        if new_password is None:
            raise serializers.ValidationError(
                {"new_password": ["new_password field is required"]}
            )
        instance.set_password(new_password)
        instance.save()
        return Response(
            {"message": "password reset successfully"}, status=status.HTTP_200_OK
        )


class RegistrationView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        user_account = serializer.save()
        signals.user_registered.send(self.__class__, user=user_account, request=request)
        return Response(
            data={
                "message": "Registration successful",
                "username": user_account.username,
                "email": user_account.email,
            },
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class ChangePasswordView(generics.UpdateAPIView):

    permission_classes = (IsAuthenticated, IsOwnProfile)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {"data": response.data, "message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class AuthTokenObtainPairView(TokenObtainPairView):
    """Return JWT tokens (access and refresh) for specific user based on username and password."""

    serializer_class = TokenObtainLifetimeSerializer


class AuthTokenRefreshView(TokenRefreshView):
    """Renew tokens (access and refresh) with new expire time based on specific user's access token."""

    serializer_class = TokenRefreshLifetimeSerializer
