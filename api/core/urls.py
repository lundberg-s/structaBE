from django.contrib import admin
from django.contrib import admin
from django.urls import path, include
from core.views.token_views import CookieTokenObtainPairView, CookieTokenRefreshView, CookieTokenVerifyView, LogoutView
from django.conf import settings

API_PREFIX = "api/"

urlpatterns = [
    path(f"{API_PREFIX}login/", CookieTokenObtainPairView.as_view(), name="login"),
    path(f"{API_PREFIX}refresh/", CookieTokenRefreshView.as_view(), name="refresh_token"),
    path(f"{API_PREFIX}verify/", CookieTokenVerifyView.as_view(), name="verify_token"),
    path(f"{API_PREFIX}logout/", LogoutView.as_view(), name="logout"),
    path(f"{API_PREFIX}admin/", admin.site.urls),
    path(f"{API_PREFIX}", include("users.urls")),
    path(f"{API_PREFIX}", include("engagements.urls")),
    path(f"{API_PREFIX}", include("relations.urls")),
    path(f"{API_PREFIX}core/", include("core.urls_app")),
]

# Add debug toolbar URLs in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
