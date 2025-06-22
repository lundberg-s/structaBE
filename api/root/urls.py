from django.contrib import admin
from django.urls import path, include
from root.views import CookieTokenObtainPairView, CookieTokenRefreshView, CookieTokenVerifyView, LogoutView

API_PREFIX = "api/"

urlpatterns = [
    path(f"{API_PREFIX}login/", CookieTokenObtainPairView.as_view(), name="login"),
    path(f"{API_PREFIX}refresh/", CookieTokenRefreshView.as_view(), name="refresh_token"),
    path(f"{API_PREFIX}verify/", CookieTokenVerifyView.as_view(), name="verify_token"),
    path(f"{API_PREFIX}logout/", LogoutView.as_view(), name="logout"),
    path(f"{API_PREFIX}admin/", admin.site.urls),
    path(f"{API_PREFIX}user/", include("user.urls")),
]
