from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import models


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


class Event(models.Model):
    name = models.CharField(max_length=50)
    starting_date = models.DateTimeField()

    def __str__(self):
        return self.name
