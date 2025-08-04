from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from relations.models import Relation
from relations.serializers.relation_serializers import RelationSerializer
from core.views.base_views import BaseView


class RelationListCreateView(BaseView, generics.ListCreateAPIView):
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.get_tenant_queryset(Relation)

    def perform_create(self, serializer):
        relation = serializer.save(tenant=self.get_tenant(), created_by=self.get_user().id)
        self._log_activity(relation, "created", "created")

    def _log_activity(self, instance, activity_type, action_text):
        """Log activity for relations."""
        self.log_activity(instance, activity_type, action_text)


class RelationDetailView(BaseView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.get_tenant_queryset(Relation)

    def check_object_permissions(self, request, obj):
        """Override to use simpler permissions for relations."""
        # For relations, just check if the object belongs to the user's tenant
        if obj.tenant != request.user.tenant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to access this relation.")

    def perform_update(self, serializer):
        relation = serializer.save()
        self._log_activity(relation, "updated", "updated")

    def perform_destroy(self, instance):
        self._log_activity(instance, "deleted", "deleted")
        instance.delete()

    def _log_activity(self, instance, activity_type, action_text):
        """Log activity for relations."""
        self.log_activity(instance, activity_type, action_text) 