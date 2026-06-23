from django.urls import path

from .views import AuthTokenRefreshView, CurrentUserView, LoginView, LogoutView, RegisterView

app_name = "auth"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="me"),
    path("token/refresh/", AuthTokenRefreshView.as_view(), name="token-refresh"),
]

