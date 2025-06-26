from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from django_filters.rest_framework import DjangoFilterBackend

from diarium.models import Case, ActivityLog
from diarium.serializers import CaseSerializer, CaseCreateSerializer, CaseUpdateSerializer

class CaseListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'priority', 'assigned_user']
    search_fields = ['title', 'description']

    
    def get_queryset(self):
        return Case.objects.select_related('assigned_user', 'created_by').prefetch_related(
            'attachments', 'comments', 'activity_log'
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CaseCreateSerializer
        return CaseSerializer
    
    def perform_create(self, serializer):
        case = serializer.save(created_by=self.request.user)
        
        # Create activity log entry
        ActivityLog.objects.create(
            case=case,
            user=self.request.user,
            activity_type='created',
            description=f'Case "{case.title}" was created'
        )

class CaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Get case by ID
    PUT: Update case
    DELETE: Delete case
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Case.objects.select_related('assigned_user', 'created_by').prefetch_related(
            'attachments', 'comments', 'activity_log'
        )
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CaseUpdateSerializer
        return CaseSerializer
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        old_assigned_user = self.get_object().assigned_user
        
        case = serializer.save()
        
        if old_status != case.status:
            ActivityLog.objects.create(
                case=case,
                user=self.request.user,
                activity_type='status_changed',
                description=f'Status changed from "{old_status}" to "{case.status}"'
            )
        
        if old_assigned_user != case.assigned_user:
            if case.assigned_user:
                ActivityLog.objects.create(
                    case=case,
                    user=self.request.user,
                    activity_type='assigned',
                    description=f'Case assigned to {case.assigned_user.username}'
                )
            else:
                ActivityLog.objects.create(
                    case=case,
                    user=self.request.user,
                    activity_type='assigned',
                    description='Case unassigned'
                )
        
        # General update log
        ActivityLog.objects.create(
            case=case,
            user=self.request.user,
            activity_type='updated',
            description=f'Case "{case.title}" was updated'
        )
    
    def perform_destroy(self, instance):
        # Create activity log before deletion
        ActivityLog.objects.create(
            case=instance,
            user=self.request.user,
            activity_type='deleted',
            description=f'Case "{instance.title}" was deleted'
        )
        instance.delete() 