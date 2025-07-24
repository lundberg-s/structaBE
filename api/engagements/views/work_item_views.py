from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import ActivityLog, WorkItem


class BaseWorkItemView:
    """Base class for work item views with tenant type checking."""

    allowed_type = None  # e.g., WorkItemType.TICKET

    def get_user(self):
        return self.request.user

    def _get_tenant(self):
        return self.request.user.tenant

    def _get_tenant_type(self):
        return self.request.user.tenant.work_item_type.lower()

    def _check_tenant_type(self):
        return self._get_tenant_type() == self.allowed_type

    def _log_activity(self, instance, activity_type, action_text):
        ActivityLog.objects.create(
            tenant=self._get_tenant(),
            work_item=instance,
            created_by=self.get_user(),
            activity_type=activity_type,
            description=f'{self.model.__name__} "{instance.title}" was {action_text}.',
        )


class BaseWorkItemListView(BaseWorkItemView, ListCreateAPIView):
    model = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        if not self._check_tenant_type():
            return self.model.objects.none()
        
        # Use the serializer's optimized queryset instead of managers.py
        base_queryset = self.model.objects.active().for_tenant(self._get_tenant())
        return self.get_serializer_class().get_optimized_queryset(base_queryset)

    def perform_create(self, serializer):
        if not self._check_tenant_type():
            return  # Optionally raise PermissionDenied
            
        instance = serializer.save(
            tenant=self._get_tenant(), created_by=self.get_user()
        )
        self._log_activity(instance, "created", "created")


class BaseWorkItemDetailView(BaseWorkItemView, RetrieveUpdateDestroyAPIView):
    model = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self._check_tenant_type():
            return self.model.objects.none()

        # Use the serializer's optimized queryset instead of managers.py
        base_queryset = self.model.objects.active().for_tenant(self._get_tenant())
        return self.get_serializer_class().get_optimized_queryset(base_queryset)

    def perform_update(self, serializer):
        if not self._check_tenant_type():
            return  # Optionally raise PermissionDenied

        instance = serializer.save(tenant=self._get_tenant())
        self._log_activity(instance, "updated", "updated")

    def perform_destroy(self, instance):
        self._log_activity(instance, "deleted", "deleted")
        instance.delete()
