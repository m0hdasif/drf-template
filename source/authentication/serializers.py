from datetime import datetime

from django.utils import timezone
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.data import Messages
from core_utils import utils

from .models import User


class StatusSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(required=True)

    class Meta:
        fields = ("is_active",)
        required_fields = fields


class UserStatusSerializer(StatusSerializer):
    class Meta(StatusSerializer.Meta):
        model = User


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    first_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}}
        }

    def validate(self, data):
        password = data["password"]
        confirm_password = data["confirm_password"]
        if password != confirm_password:
            raise ValidationError({"error": "Password does not match."})
        return data

    def save(self, **kwargs):
        data_fields = ["email", "first_name", "last_name", "avatar"]
        data = {}
        for key in data_fields:
            val = self.validated_data.get(key)
            if val is not None:
                data[key] = val

        data["username"] = data["email"]

        if self.instance is not None:
            self.instance = self.update(self.instance, data)
        else:
            self.instance = self.create(data)
        user = self.instance
        user.set_password(self.validated_data["password"])
        user.save()
        return user


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "required": False,
            },
        }
        read_only_fields = ("is_superuser", "is_staff")

    def update(self, instance, validated_data):
        validated_data["username"] = validated_data["email"]
        return super().update(instance, validated_data)

    def create(self, validated_data):
        data = validated_data.copy()
        data["username"] = data["email"]
        self.instance = super().create(data)
        if data.get("password"):
            self.instance.set_password(data["password"])
        self.instance.save()
        return self.instance


class UserProfileSerializer(UserBaseSerializer):
    pass


class UserSerializer(UserBaseSerializer):
    username = serializers.CharField(read_only=True, required=False)

    class Meta(UserBaseSerializer.Meta):
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "avatar",
            "password",
            "is_internal",
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("old_password", "new_password", "confirm_password")

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()

        return instance


class UserActivationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        "invalid_token": Messages.INVALID_TOKEN_ERROR,
        "invalid_uid": Messages.INVALID_UID_ERROR,
    }

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        try:
            uid = utils.decode_str(self.initial_data.get("uid", ""))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_uid"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )

        if self.is_token_valid(user, self.initial_data.get("token", "")):
            if not (user.email_verified and user.is_active):
                return validated_data
            raise exceptions.PermissionDenied({"token": Messages.STALE_TOKEN_ERROR})
        else:
            key_error = "invalid_token"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )

    def is_token_valid(self, user, token):
        return self.context["view"].token_generator.check_token(user, token)


class TokenSerializerMixin:
    def get_refresh_token(self, attrs):
        """Get refresh token in the token serializer derived class."""
        raise NotImplementedError

    def validate_token(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_refresh_token(attrs)
        data["exp"] = timezone.datetime.fromtimestamp(
            refresh.access_token.payload["exp"]
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        data["refresh_exp"] = datetime.fromtimestamp(refresh.payload["exp"]).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        data["lifetime"] = int(refresh.access_token.lifetime.total_seconds())
        data["refresh_lifetime"] = int(refresh.lifetime.total_seconds())
        return data


class TokenObtainLifetimeSerializer(TokenSerializerMixin, TokenObtainPairSerializer):
    def validate(self, attrs):
        return self.validate_token(attrs)

    def get_refresh_token(self, attrs):
        return self.get_token(self.user)


class TokenRefreshLifetimeSerializer(TokenSerializerMixin, TokenRefreshSerializer):
    def validate(self, attrs):
        return self.validate_token(attrs)

    def get_refresh_token(self, attrs):
        return RefreshToken(attrs["refresh"])
