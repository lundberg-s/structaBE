from django.urls import path


from relations.views.relation_views import RelationListCreateView, RelationDetailView
from relations.views.audit_views import RelationAuditViewSet
from relations.views.assignment_views import AssignmentCreateView

app_name = "relations"

urlpatterns = [
    path("relations/", RelationListCreateView.as_view(), name="relation-list"),
    path("relations/<uuid:pk>/", RelationDetailView.as_view(), name="relation-detail"),

    path('assignments/', AssignmentCreateView.as_view(), name='assignment-create'),

    path("audit-logs/relations/", RelationAuditViewSet.as_view({'get': 'list'}), name="relation-audit-list"),
    path("audit-logs/relations/<uuid:pk>/", RelationAuditViewSet.as_view({'get': 'retrieve'}), name="relation-audit-detail"),
]
