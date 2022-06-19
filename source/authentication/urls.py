from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    AuthTokenObtainPairView,
    AuthTokenRefreshView,
    ChangePasswordView,
    LogoutView,
    RegistrationView,
    UserView,
)

router = DefaultRouter()
router.register("register", RegistrationView, basename="user-auth")
router.register("user", UserView, basename="user")

router.register(
    r"org/(?P<org_id>\d+)/register", RegistrationView, basename="org-user-auth"
)


urlpatterns = [
    path("", include(router.urls)),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", AuthTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", AuthTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "user_change_password/",
        ChangePasswordView.as_view(),
        name="auth_change_password",
    ),
    path(
        "user_reset_password/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
]
