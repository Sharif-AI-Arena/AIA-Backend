from django.contrib import admin
from staff.models import StaffTeam, StaffTeamMember


class StaffTeamMemberInline(admin.TabularInline):
    model = StaffTeamMember
    extra = 1
    autocomplete_fields = ["staff"]
    fields = ("staff", "role")


@admin.register(StaffTeam)
class StaffTeamAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "description", "member_count")
    list_filter = ("event",)
    search_fields = ("name", "description")
    inlines = [StaffTeamMemberInline]

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Members"


@admin.register(StaffTeamMember)
class StaffTeamMemberAdmin(admin.ModelAdmin):
    list_display = ("staff", "staff_team", "role")
    list_filter = ("role", "staff_team__name", "staff_team__event")
    search_fields = (
        "staff__user__email",
        "staff__info__first_name",
        "staff__info__last_name",
    )
    autocomplete_fields = ["staff", "staff_team"]
