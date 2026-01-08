from core.models import Event
from django.db import models
from participant.models import Participant


class StaffTeam(models.Model):
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=200, blank=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="staff_teams"
    )

    def __str__(self) -> str:
        return f"{self.event} - {self.name}"

    class Meta:
        unique_together = ("event", "name")


class StaffTeamMember(models.Model):
    ROLE_CHOICES = (("H", "Head"), ("S", "SubHead"), ("M", "Member"))

    staff = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="staff_teams"
    )
    staff_team = models.ForeignKey(
        StaffTeam, on_delete=models.CASCADE, related_name="members"
    )
    role = models.CharField(max_length=1, default="M", choices=ROLE_CHOICES)

    def __str__(self) -> str:
        return f"{self.staff} - {self.role} of {self.staff_team} Team"

    class Meta:
        unique_together = ("staff", "staff_team")
