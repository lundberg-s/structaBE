from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import WorkItem
from core.views.base_views import BaseView


class BaseWorkItemView(BaseView):
    """Base class for work item views with tenant type checking."""

    allowed_type = None  # e.g., WorkItemType.TICKET

    def _get_tenant_type(self):
        return self.get_tenant().work_item_type.lower()

    def _check_tenant_type(self):
        return self._get_tenant_type() == self.allowed_type

    def _log_activity(self, instance, activity_type, action_text):
        """Log activity for work items."""
        self.log_activity(instance, activity_type, action_text)


class BaseWorkItemListView(BaseWorkItemView, ListCreateAPIView):
    model = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = []
    search_fields = []
    ordering_fields = []

    def get_queryset(self):
        if not self._check_tenant_type():
            return self.model.objects.none()
        
        # Use the serializer's optimized queryset instead of managers.py
        base_queryset = self.model.objects.active().for_tenant(self.get_tenant())
        return self.get_serializer_class().get_optimized_queryset(base_queryset)

    def perform_create(self, serializer):
        if not self._check_tenant_type():
            return  # Optionally raise PermissionDenied
            
        instance = serializer.save(
            tenant=self.get_tenant(), created_by=self.get_user()
        )
        self._log_activity(instance, "created", "created")


class BaseWorkItemDetailView(BaseWorkItemView, RetrieveUpdateDestroyAPIView):
    model = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self._check_tenant_type():
            return self.model.objects.none()

        # Use the serializer's optimized queryset instead of managers.py
        base_queryset = self.model.objects.active().for_tenant(self.get_tenant())
        return self.get_serializer_class().get_optimized_queryset(base_queryset)

    def perform_update(self, serializer):
        if not self._check_tenant_type():
            return  # Optionally raise PermissionDenied

        instance = serializer.save(tenant=self.get_tenant())
        self._log_activity(instance, "updated", "updated")

    def perform_destroy(self, instance):
        self._log_activity(instance, "deleted", "deleted")
        instance.delete()
