from random import choices

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404
from drf_spectacular.utils import extend_schema, extend_schema_view
from participant.models import Participant, Participation, ParticipationPlan
from participant.serializers import (
    ParticipantInfoSerializer,
    ParticipantSerializer,
    ParticipationPlanSerializer,
    ParticipationSerializer,
)
from rest_framework import generics, permissions, serializers, status, views
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response


class ParticipantCreateAPIView(generics.CreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=ParticipantSerializer,
        responses={201: ParticipantSerializer},
        description="Create a new participant (user + participant info)",
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user_data = response.data.get("user")
        if isinstance(user_data, dict) and "password" in user_data:
            user_data.pop("password")
        return response


@extend_schema_view(
    get=extend_schema(
        responses={200: ParticipantInfoSerializer},
        description="Retrieve the authenticated participant's personal info",
    ),
    put=extend_schema(
        request={"multipart/form-data": ParticipantInfoSerializer},
        responses={200: ParticipantInfoSerializer},
        description="Update the authenticated participant's personal info",
    ),
)
class ParticipantInfoRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "put", "head", "options"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        try:
            participant = Participant.objects.get(user=self.request.user)
        except Participant.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, participant)
        return participant.info


class PasswordResetAPIView(views.APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    @extend_schema(
        request=serializers.Serializer,
        responses={200: str},
        description="Request a password reset token for the given email (POST).",
    )
    def post(self, request):
        try:
            participant = Participant.objects.get(user__email=request.data["email"])
        except Participant.DoesNotExist:
            raise Http404
        except Participant.MultipleObjectsReturned:
            return Response(
                "Multiple users found with this email address",
                status=status.HTTP_400_BAD_REQUEST,
            )
        participant.password_reset_code = "".join(
            choices([str(i) for i in range(10)], k=10)
        )
        participant.save()

        reset_link = (
            f"https://aia-sharif.com/reset-password/{participant.password_reset_code}"
        )
        message = f"Your AIA password reset link is: {reset_link}"

        email = EmailMessage(
            subject="AIA Password Reset",
            body=message,
            from_email=settings.SERVER_EMAIL,
            to=[participant.user.email],
            headers={"x-liara-tag": "password-reset"},
        )

        email.send(fail_silently=False)

        return Response(
            f"Password reset code sent to the email address ({participant.user.email})",
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=serializers.Serializer,
        responses={200: str},
        description="Confirm password reset with token and set new password (PUT).",
    )
    def put(self, request):
        try:
            participant = Participant.objects.get(user__email=request.data["email"])
        except Participant.DoesNotExist:
            raise Http404
        except Participant.MultipleObjectsReturned:
            return Response(
                "Mutiple Users found with this Email Address",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not participant.password_reset_code:
            return Response(
                "Password reset code is not set for this user. "
                "Or the password is already changed with that code.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif participant.password_reset_code == request.data["token"]:
            participant.user.set_password(request.data["password"])
            participant.user.save()
            participant.password_reset_code = None
            participant.save()
            return Response("Password reset successfully", status=status.HTTP_200_OK)
        else:
            return Response(
                "Password reset code is not correct",
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class ParticipantPasswordChangeAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=serializers.Serializer,
        responses={200: str},
        description="Change password for authenticated participant (PUT).",
    )
    def put(self, request):
        participant = Participant.objects.get(user=request.user)
        if not participant.user.check_password(request.data["old_password"]):
            return Response(
                "Old password is not correct", status=status.HTTP_406_NOT_ACCEPTABLE
            )
        participant.user.set_password(request.data["new_password"])
        participant.user.save()
        return Response("Password changed successfully", status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        responses={200: ParticipationSerializer(many=True)},
        description="List participations for the authenticated participant for a given event",
    )
)
class ParticipationByEventAPIView(generics.ListAPIView):
    serializer_class = ParticipationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Participation.objects.filter(
            plan__event=self.kwargs["event_id"], participant=self.kwargs["participant"]
        )

    def get(self, request, *args, **kwargs):
        try:
            self.kwargs["participant"] = Participant.objects.get(user=self.request.user)
        except Participant.DoesNotExist:
            raise Http404
        return self.list(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        responses={200: ParticipationPlanSerializer(many=True)},
        description="List available participation plans for an event",
    )
)
class ParticipationPlanByEventAPIView(generics.ListAPIView):
    queryset = ParticipationPlan.objects.all()
    serializer_class = ParticipationPlanSerializer

    def get_queryset(self):
        return ParticipationPlan.objects.filter(event=self.kwargs["event_id"])


@extend_schema_view(
    get=extend_schema(
        responses={200: ParticipationPlanSerializer(many=True)},
        description="List participation plans for an event (mode of attendance view)",
    )
)
class ModeOfAttendanceByEventAPIView(generics.ListAPIView):
    queryset = ParticipationPlan.objects.all()
    serializer_class = ParticipationPlanSerializer

    def get_queryset(self):
        return ParticipationPlan.objects.filter(event=self.kwargs["event_id"])
