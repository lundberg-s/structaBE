from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models import AuditLog
from core.serializers.audit_serializers import AuditLogSerializer
from users.permissions import CanViewContentOnly


class BaseAuditViewSet(ReadOnlyModelViewSet):
    """
    Generic base class for audit viewsets.
    Provides shared functionality without app-specific knowledge.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, CanViewContentOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activity_type', 'created_by', 'created_at', 'compliance_category', 'risk_level']
    search_fields = ['description', 'entity_name', 'business_process']
    ordering_fields = ['created_at', 'activity_type', 'entity_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get audit logs filtered by tenant.
        Subclasses should override to add entity-specific filtering.
        """
        return AuditLog.objects.filter(
            tenant=self.request.user.tenant
        ).select_related('created_by')
    
    def get_serializer_context(self):
        """Add request context to serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context 