from django.contrib import admin
from participant.models import (
    ModeOfAttendance,
    Participant,
    ParticipantInfo,
    Participation,
    ParticipationPlan,
)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("participant", "plan", "created_time")
    list_filter = (
        "plan",
        "plan__mode_of_attendance",
        "plan__mode_of_attendance__has_lunch",
    )
    search_fields = ("participant__user__email",)


class ParticipationPlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "price",
        "mode_of_attendance",
    )
    list_filter = ("event",)
    search_fields = ("event__name",)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("__str__", "get_email")
    search_fields = ("user__email", "info__national_code", "info__phone_number")
    readonly_fields = ("user", "info")

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"


class ParticipantInfoAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "national_code", "phone_number")
    search_fields = ("first_name", "last_name", "national_code", "phone_number")


class ModeOfAttendanceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_national_code_required", "has_lunch")
    list_filter = ("is_national_code_required", "has_lunch")
    search_fields = ("name",)


admin.site.register(ModeOfAttendance, ModeOfAttendanceAdmin)
admin.site.register(ParticipationPlan, ParticipationPlanAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(ParticipantInfo, ParticipantInfoAdmin)
admin.site.register(Participation, ParticipationAdmin)
