import random
from datetime import timedelta

from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from core.models import Event, EmailVerification
from core.serializers import (
    EventSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer, EmailCheckSerializer, EmailPasswordLoginSerializer, VerifyEmailAndSignupSerializer,
)
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView


def send_verification_code(email: str) -> None:
    existing = EmailVerification.objects.filter(email=email).first()

    if existing and not existing.is_expired:
        raise ValidationError(
            {
                "detail": "Verification code already sent.",
                "retry_after_seconds": existing.remaining_seconds,
            }
        )

    # if
    EmailVerification.objects.filter(email=email).delete()

    code = str(random.randint(100000, 999999))

    EmailVerification.objects.create(
        email=email,
        code=code,
    )

    print(f"[DEV] Verification code for {email}: {code}")

class EmailCheckAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailCheckSerializer,
        responses=EmailCheckSerializer,
        description="Check email and auto-send verification code if new user",
    )
    def post(self, request):
        serializer = EmailCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        exists = User.objects.filter(email=email).exists()

        code_sent = False
        if not exists:
            send_verification_code(email)
            code_sent = True

        return Response(
            {
                "exists": exists,
                "code_sent": code_sent,
            },
            status=status.HTTP_200_OK,
        )


class EmailPasswordLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailPasswordLoginSerializer,
        responses=EmailPasswordLoginSerializer,
        description="Login with email and password",
    )

    def post(self, request):
        serializer = EmailPasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )

class VerifyEmailAndSignupAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyEmailAndSignupSerializer,
        responses=VerifyEmailAndSignupSerializer,
        description="Verify email and signup code",
    )

    def post(self, request):
        serializer = VerifyEmailAndSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.validated_data,
            status=status.HTTP_201_CREATED,
        )


class NextEventAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: EventSerializer, 404: None},
        description="Return the nearest upcoming event (starting_date > now)",
    )
    def get(self, request, *args, **kwargs):
        event = (
            Event.objects.filter(starting_date__gt=timezone.now())
            .order_by("starting_date")
            .first()
        )
        if not event:
            return Response(
                {"detail": "No upcoming event found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = EventSerializer(event, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """Token refresh endpoint with OpenAPI schema annotations."""

    @extend_schema(
        request=TokenRefreshRequestSerializer,
        responses={200: TokenRefreshResponseSerializer},
        description="Refresh access token using a refresh token",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
