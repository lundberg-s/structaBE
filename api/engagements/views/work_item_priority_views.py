from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from engagements.models import WorkItemPriority
from engagements.serializers.work_item_priority_serializers import (
    WorkItemPrioritySerializer,
    WorkItemPriorityListSerializer,
    WorkItemPriorityCreateSerializer,
    WorkItemPriorityUpdateSerializer,
)
from core.views.base_views import BaseView
from rest_framework.permissions import IsAuthenticated


class WorkItemPriorityViewSet(BaseView, viewsets.ModelViewSet):
    """ViewSet for managing work item priority options."""
    
    model = WorkItemPriority
    serializer_class = WorkItemPrioritySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['label', 'translated_label']
    ordering_fields = ['label', 'sort_order', 'created_at']
    ordering = ['sort_order', 'label']
    
    def get_queryset(self):
        """Filter by tenant."""
        return WorkItemPriority.objects.filter(
            tenant=self.request.user.tenant,
            is_active=True
        ).select_related('tenant')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return WorkItemPriorityListSerializer
        elif self.action == 'create':
            return WorkItemPriorityCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkItemPriorityUpdateSerializer
        return WorkItemPrioritySerializer
    
    def perform_create(self, serializer):
        """Set tenant automatically."""
        serializer.save(tenant=self.request.user.tenant) 