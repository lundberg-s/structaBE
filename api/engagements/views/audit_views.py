from core.views.base_audit_views import BaseAuditViewSet


class WorkItemAuditViewSet(BaseAuditViewSet):
    """
    Audit viewset for work items (tickets, cases, jobs).
    Owned by the engagements app.
    """
    
    def get_queryset(self):
        """
        Get audit logs for work items only.
        Filters by work item entity types.
        """
        return super().get_queryset().filter(
            entity_type__in=['workitem', 'ticket', 'case', 'job']
        )
    
    def get_serializer_context(self):
        """Add work item specific context."""
        context = super().get_serializer_context()
        context['entity_type'] = 'workitem'
        return context 