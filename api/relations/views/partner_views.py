from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from relations.models import Partner

from core.views.base_views import BaseView

class PartnerListView(BaseView, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return self.get_tenant_queryset(Partner)

    def perform_create(self, serializer):
        partner = serializer.save(tenant=self.get_tenant(), created_by=self.get_user())
        self._log_activity(partner, "created", "created")

    def _log_activity(self, instance, activity_type, action_text):
        """Log activity for partners."""
        self.log_activity(instance, activity_type, action_text)


class PartnerDetailView(BaseView, RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.get_tenant_queryset(Partner)

    def check_object_permissions(self, request, obj):
        """Override to use simpler permissions for partners."""
        # For partners, just check if the object belongs to the user's tenant
        if obj.tenant != request.user.tenant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to access this partner.")

    def perform_update(self, serializer):
        partner = serializer.save()
        self._log_activity(partner, "updated", "updated")

    def perform_destroy(self, instance):
        self._log_activity(instance, "deleted", "deleted")
        instance.delete()

    def _log_activity(self, instance, activity_type, action_text):
        """Log activity for partners."""
        self.log_activity(instance, activity_type, action_text)