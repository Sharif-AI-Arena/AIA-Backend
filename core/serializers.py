import random

from django.core.cache import cache

from core import models
from core.models import Event
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()
    exists = serializers.BooleanField(read_only=True)
    code_sent = serializers.BooleanField(read_only=True)


class EmailPasswordLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        user = authenticate(
            email=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class VerifyEmailAndSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField(min_length=8)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        print(models.EmailVerification.objects.filter(email=attrs["email"], code=attrs["code"]))
        if not models.EmailVerification.objects.filter(email=attrs["email"], code=attrs["code"]).exists():
            raise serializers.ValidationError("Invalid verification code")

        user = User.objects.create_user(
            email=attrs["email"],
            username=attrs["username"],
            password=attrs["password"],
            is_active=True,
        )

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = CharField(write_only=True)

class TokenRefreshResponseSerializer(serializers.Serializer):
    access = CharField(read_only=True)


# class CustomTokenObtainPairSerializer(serializers.Serializer):
#     email = serializers.EmailField(write_only=True)
#     password = serializers.CharField(write_only=True)
#     access = serializers.CharField(read_only=True)
#     refresh = serializers.CharField(read_only=True)
#
#     def validate(self, attrs):
#         email = attrs.get("email")
#         password = attrs.get("password")
#         user = authenticate(
#             request=self.context.get("request"), email=email, password=password
#         )
#         if not user:
#             raise serializers.ValidationError(
#                 "No active account found with the given credentials"
#             )
#         refresh = RefreshToken.for_user(user)
#         return {"refresh": str(refresh), "access": str(refresh.access_token)}


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
