from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from engagements.models import WorkItemStatus
from engagements.serializers.work_item_status_serializers import (
    WorkItemStatusSerializer,
    WorkItemStatusListSerializer,
    WorkItemStatusCreateSerializer,
    WorkItemStatusUpdateSerializer,
)
from core.views.base_views import BaseView
from rest_framework.permissions import IsAuthenticated


class WorkItemStatusViewSet(BaseView, viewsets.ModelViewSet):
    """ViewSet for managing work item status options."""
    
    model = WorkItemStatus
    serializer_class = WorkItemStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['label', 'translated_label']
    ordering_fields = ['label', 'sort_order', 'created_at']
    ordering = ['sort_order', 'label']
    
    def get_queryset(self):
        """Filter by tenant."""
        return WorkItemStatus.objects.filter(
            tenant=self.request.user.tenant,
            is_active=True
        ).select_related('tenant')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return WorkItemStatusListSerializer
        elif self.action == 'create':
            return WorkItemStatusCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkItemStatusUpdateSerializer
        return WorkItemStatusSerializer
    
    def perform_create(self, serializer):
        """Set tenant automatically."""
        serializer.save(tenant=self.request.user.tenant) 