from core.views.base_audit_views import BaseAuditViewSet

class RelationAuditViewSet(BaseAuditViewSet):
    """
    Audit viewset for relations.
    Owned by the relations app.
    """
    
    def get_queryset(self):
        """
        Get audit logs for relations only.
        """
        return super().get_queryset().filter(
            entity_type='relation'
        )
    
    def get_serializer_context(self):
        """Add relation specific context."""
        context = super().get_serializer_context()
        context['entity_type'] = 'relation'
        return context 