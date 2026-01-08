from core.views import EmailTokenObtainPairView, NextEventAPIView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("sign-in/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("sign-in/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("next-event/", NextEventAPIView.as_view(), name="next-event"),
]
