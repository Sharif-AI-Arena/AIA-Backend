from rest_framework import serializers
from staff.models import StaffTeam, StaffTeamMember


class StaffTeamMemberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="staff.user.id", read_only=True)
    email = serializers.EmailField(source="staff.user.email", read_only=True)
    first_name = serializers.CharField(source="staff.info.first_name", read_only=True)
    last_name = serializers.CharField(source="staff.info.last_name", read_only=True)
    github = serializers.URLField(source="staff.info.github", read_only=True)
    linkedin = serializers.URLField(source="staff.info.linkedin", read_only=True)

    class Meta:
        model = StaffTeamMember
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "github",
            "linkedin",
            "role",
        )


class StaffTeamSerializer(serializers.ModelSerializer):
    members = StaffTeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = StaffTeam
        fields = ("id", "name", "description", "members")
