from django.urls import path
from core.views.role_views import RoleListCreateView, RoleDetailView

app_name = "core"

urlpatterns = [
    path("roles/", RoleListCreateView.as_view(), name="role-list"),
    path("roles/<uuid:pk>/", RoleDetailView.as_view(), name="role-detail"),
] 