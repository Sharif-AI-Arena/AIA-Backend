from core import views
from django.urls import path
from core.google_login import GoogleTokenObtainAPIView
from core.views import EmailCheckAPIView, EmailPasswordLoginAPIView, VerifyEmailAndSignupAPIView

urlpatterns = [
    path("auth/email/check/", EmailCheckAPIView.as_view()),
    path("auth/email/login/", EmailPasswordLoginAPIView.as_view()),
    path("auth/email/verify/", VerifyEmailAndSignupAPIView.as_view()),
    path("sign-in/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("next-event/", views.NextEventAPIView.as_view(), name="next-event"),
    path("auth/login/google/", GoogleTokenObtainAPIView.as_view()),
]