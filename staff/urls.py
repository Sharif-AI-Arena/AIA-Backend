from django.urls import path
from staff import views

urlpatterns = [
    path(
        "teams/<int:event_id>/",
        views.StaffTeamsByEventAPIView.as_view(),
        name="staff-teams-by-event",
    ),
]
