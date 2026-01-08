from core.models import Event
from core.serializers import CustomTokenObtainPairSerializer, EventSerializer
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class EmailTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=CustomTokenObtainPairSerializer,
        responses={200: CustomTokenObtainPairSerializer},
        description="Obtain JWT access and refresh tokens using email and password",
    )
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
