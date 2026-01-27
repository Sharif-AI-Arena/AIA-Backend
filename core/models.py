from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import models
from django.utils import timezone


class EmailModelBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


class EmailVerification(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=self.EXPIRE_MINUTES)

    @property
    def remaining_seconds(self):
        expire_time = self.created_at + timedelta(minutes=self.EXPIRE_MINUTES)
        delta = expire_time - timezone.now()
        return max(0, int(delta.total_seconds()))

    def __str__(self):
        return f"{self.email} - {self.code}"

class Event(models.Model):
    name = models.CharField(max_length=50)
    starting_date = models.DateTimeField()

    def __str__(self):
        return self.name
