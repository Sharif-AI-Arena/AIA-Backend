from core.models import Event
from django.contrib import admin


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "starting_date")


admin.site.register(Event, EventAdmin)
