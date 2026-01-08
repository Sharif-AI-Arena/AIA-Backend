from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions
from staff.models import StaffTeam
from staff.serializers import StaffTeamSerializer


@extend_schema_view(
    get=extend_schema(
        responses={200: StaffTeamSerializer(many=True)},
        description="List all staff teams with their members for a given event",
    )
)
class StaffTeamsByEventAPIView(generics.ListAPIView):
    serializer_class = StaffTeamSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return StaffTeam.objects.filter(event_id=event_id).prefetch_related(
            "members__staff__user", "members__staff__info"
        )
