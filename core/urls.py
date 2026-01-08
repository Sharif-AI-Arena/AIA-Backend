from core import views
from django.urls import path

urlpatterns = [
    path(
        "sign-in/", views.EmailTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "sign-in/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    path("next-event/", views.NextEventAPIView.as_view(), name="next-event"),
]
