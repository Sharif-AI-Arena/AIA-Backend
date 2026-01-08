import uuid

from core.models import Event
from django.contrib.auth.models import User
from django.db import models
from django.utils.deconstruct import deconstructible


@deconstructible
class UniqueUploadPath:
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        return f"{self.sub_path}/{uuid.uuid4()}.{ext}"


class ParticipantInfo(models.Model):
    GENDER_CHOICES = (("M", "Male"), ("F", "Female"), ("O", "Other"))

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    first_name_persian = models.CharField(max_length=100, blank=True)
    last_name_persian = models.CharField(max_length=100, blank=True)

    phone_number = models.CharField(max_length=15)
    national_code = models.CharField(max_length=10)
    university = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, default="M", choices=GENDER_CHOICES)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    image = models.ImageField(upload_to="participants/", blank=True, null=True)
    github = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)

    student_id = models.CharField(max_length=15, blank=True)
    taken_courses = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.national_code}"


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    info = models.ForeignKey(
        ParticipantInfo, on_delete=models.SET_NULL, null=True, blank=True
    )
    password_reset_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        if self.info:
            return f"{self.info.first_name} {self.info.last_name} - {self.user.email}"
        else:
            return f"NO INFO - user: {self.user}"


class ModeOfAttendance(models.Model):
    name = models.CharField(max_length=50)
    is_national_code_required = models.BooleanField(default=False)
    has_lunch = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {'with lunch' if self.has_lunch else 'without lunch'}"


class ParticipationPlan(models.Model):
    price = models.IntegerField(default=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    mode_of_attendance = models.ForeignKey(
        ModeOfAttendance, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.event} - {self.mode_of_attendance}"


class Participation(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    plan = models.ForeignKey(ParticipationPlan, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant} - {self.plan}"
