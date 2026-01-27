from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

from core.google import verify_google_id_token


class GoogleTokenObtainAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id_token": {"type": "string"},
                },
                "required": ["id_token"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "is_new_user": {"type": "boolean"},
                },
            }
        },
        description="Google OAuth login/signup (single endpoint)",
    )
    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response(
                {"detail": "id_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_user = verify_google_id_token(token)
        if not google_user:
            return Response(
                {"detail": "Invalid Google token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        User = get_user_model()

        user, created = User.objects.get_or_create(
            email=google_user["email"],
            defaults={
                "first_name": google_user["full_name"],
            },
        )

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )
