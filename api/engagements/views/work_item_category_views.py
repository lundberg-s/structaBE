from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from engagements.models import WorkItemCategory
from engagements.serializers.work_item_category_serializers import (
    WorkItemCategorySerializer,
    WorkItemCategoryListSerializer,
    WorkItemCategoryCreateSerializer,
    WorkItemCategoryUpdateSerializer,
)
from core.views.base_views import BaseView
from rest_framework.permissions import IsAuthenticated


class WorkItemCategoryViewSet(BaseView, viewsets.ModelViewSet):
    """ViewSet for managing work item category options."""
    
    model = WorkItemCategory
    serializer_class = WorkItemCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['label', 'translated_label']
    ordering_fields = ['label', 'sort_order', 'created_at']
    ordering = ['sort_order', 'label']
    
    def get_queryset(self):
        """Filter by tenant."""
        return WorkItemCategory.objects.filter(
            tenant=self.request.user.tenant,
            is_active=True
        ).select_related('tenant')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return WorkItemCategoryListSerializer
        elif self.action == 'create':
            return WorkItemCategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkItemCategoryUpdateSerializer
        return WorkItemCategorySerializer
    
    def perform_create(self, serializer):
        """Set tenant automatically."""
        serializer.save(tenant=self.request.user.tenant) 