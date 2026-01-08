import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from participant.models import (
    ModeOfAttendance,
    Participant,
    ParticipantInfo,
    Participation,
    ParticipationPlan,
)
from rest_framework import serializers


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value: str) -> str:
        return make_password(value)


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Participant
        fields = ("user",)

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        if User.objects.filter(email=user_data["email"]).exists():
            raise serializers.ValidationError("User with this email already exists.")
        user_data["username"] = user_data["email"].replace("@", "_").replace(".", "_")
        password = user_data.pop("password", None)
        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
        participant = Participant.objects.create(user=user, **validated_data)
        participant.info = ParticipantInfo.objects.create()
        participant.save()
        return participant


class ParticipantInfoSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ParticipantInfo
        fields = "__all__"

    def get_email(self, obj) -> str:
        participant = Participant.objects.filter(info=obj).first()
        if participant and participant.user:
            return participant.user.email
        return None

    def validate_national_code(self, value: str) -> str:
        if value == "":
            return value
        if re.match(r"^\d{8,10}$", value):
            if len(value) < 10:
                value = "0" * (10 - len(value)) + value
            temp = 0
            for i in range(9):
                temp += int(value[i]) * (10 - i)
            rem = temp % 11
            if (rem < 2 and int(value[9]) == rem) or (
                rem >= 2 and int(value[9]) == (11 - rem)
            ):
                return value
            raise serializers.ValidationError("National Code is not valid.")
        raise serializers.ValidationError("National Code is not valid.")

    def validate_phone_number(self, value: str) -> str:
        if re.match(r"^(\+\d{1,3}|0)\d{10}$", value):
            return value
        raise serializers.ValidationError("Phone number is not valid.")

    def validate_gender(self, value: str) -> str:
        if value in ["M", "F", "O"]:
            return value
        raise serializers.ValidationError("Gender is not valid.")


class ModeOfAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeOfAttendance
        fields = "__all__"


class ParticipationSerializer(serializers.ModelSerializer):
    plan = serializers.IntegerField(source="plan.id", read_only=True)

    class Meta:
        model = Participation
        fields = ("plan",)


class ParticipationPlanSerializer(serializers.ModelSerializer):
    event = serializers.CharField(source="event.name", read_only=True)
    mode_of_attendance = ModeOfAttendanceSerializer()

    class Meta:
        model = ParticipationPlan
        fields = ("id", "price", "event", "mode_of_attendance")
