from django.urls import path

from partners.views import (
    PersonListView,
    PersonDetailView,
    OrganizationListView,
    OrganizationDetailView,
    PartnerAuditViewSet,
)

app_name = "partners"

urlpatterns = [
    path("persons/", PersonListView.as_view(), name="person-list"),
    path("persons/<uuid:pk>/", PersonDetailView.as_view(), name="person-detail"),
    path("organizations/", OrganizationListView.as_view(), name="organization-list"),
    path(
        "organizations/<uuid:pk>/",
        OrganizationDetailView.as_view(),
        name="organization-detail",
    ),
    # Audit logs for partners
    path(
        "audit-logs/partners/",
        PartnerAuditViewSet.as_view({"get": "list"}),
        name="partner-audit-list",
    ),
    path(
        "audit-logs/partners/<uuid:pk>/",
        PartnerAuditViewSet.as_view({"get": "retrieve"}),
        name="partner-audit-detail",
    ),
]
