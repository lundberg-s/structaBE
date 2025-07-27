from django.urls import path

from relations.views.person_views import PersonListView, PersonDetailView
from relations.views.organization_views import OrganizationListView, OrganizationDetailView
from relations.views.relation_views import RelationListCreateView, RelationDetailView

app_name = "relations"

urlpatterns = [
    path("persons/", PersonListView.as_view(), name="person-list"),
    path("persons/<uuid:pk>/", PersonDetailView.as_view(), name="person-detail"),

    path("organizations/", OrganizationListView.as_view(), name="organization-list"),
    path("organizations/<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),



    path("relations/", RelationListCreateView.as_view(), name="relation-list"),
    path("relations/<uuid:pk>/", RelationDetailView.as_view(), name="relation-detail"),
]
