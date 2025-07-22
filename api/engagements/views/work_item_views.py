from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from engagements.serializers.ticket_serializers import TicketSerializer, TicketWritableSerializer
from engagements.serializers.job_serializers import JobSerializer
from engagements.serializers.case_serializers import CaseSerializer

from engagements.models import Ticket, Job, Case, WorkItem, ActivityLog

from core.models import WorkItemType


class BaseWorkItemListView(ListCreateAPIView):
    model = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    allowed_type = None

    def get_queryset(self):
        if self.request.user.tenant.work_item_type.lower() != self.allowed_type:
            return self.model.objects.none()
        
        base_queryset = self.model.objects.active().filter(tenant=self.request.user.tenant)
        
        # For list view (GET), use minimal prefetching
        if self.request.method == 'GET':
            return base_queryset.select_related('tenant')
        
        # For other methods, use full prefetching
        return base_queryset.select_related(
            'created_by__partner__person',
            'tenant'
        ).prefetch_related(
            'assignments__user__partner__person',
            'attachments',
            'comments__author__partner__person',
            'activity_log__user__partner__person',
            'partner_roles__partner__person',
            'partner_roles__partner__organization'
        )

    def perform_create(self, serializer):
        if self.request.user.tenant.work_item_type.lower() == self.allowed_type:
            # Get tenant and user once to avoid repeated queries
            tenant = self.request.user.tenant
            user = self.request.user
            
            instance = serializer.save(tenant=tenant, created_by=user)
            
            # Create activity log with minimal queries
            ActivityLog.objects.create(
                tenant=tenant,
                work_item=instance,
                user=user,
                activity_type='created',
                description=f'{self.model.__name__} "{instance.title}" was created.'
            )
class BaseWorkItemDetailView(RetrieveUpdateDestroyAPIView):
    model = None
    permission_classes = [IsAuthenticated]
    allowed_type = None

    def get_queryset(self):
        if self.request.user.tenant.work_item_type.lower() != self.allowed_type:
            return self.model.objects.none()
        return self.model.objects.active().filter(tenant=self.request.user.tenant).select_related(
            'created_by__partner__person',
            'tenant'
        ).prefetch_related(
            'assignments__user__partner__person',
            'attachments',
            'comments__author__partner__person',
            'activity_log__user__partner__person',
            'partner_roles__partner__person',
            'partner_roles__partner__organization'
        )

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # Only creator can update/delete
        if request.method in ['PUT', 'PATCH', 'DELETE'] and hasattr(obj, 'created_by') and obj.created_by != request.user:
            raise PermissionDenied('You do not have permission to modify this resource.')

    def perform_update(self, serializer):
        if self.request.user.tenant.work_item_type.lower() == self.allowed_type:
            instance = serializer.save(tenant=self.request.user.tenant)
            ActivityLog.objects.create(
                tenant=self.request.user.tenant,
                work_item=instance,
                user=self.request.user,
                activity_type='updated',
                description=f'{self.model.__name__} "{instance.title}" was updated.'
            )

    def perform_destroy(self, instance):
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=instance,
            user=self.request.user,
            activity_type='deleted',
            description=f'{self.model.__name__} "{instance.title}" was deleted.'
        )
        instance.delete()


class TicketListView(BaseWorkItemListView):
    model = Ticket
    allowed_type = WorkItemType.TICKET
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            from engagements.serializers.work_item_serializers import WorkItemListSerializer
            return WorkItemListSerializer
        elif self.request.method == 'POST':
            from engagements.serializers.ticket_serializers import TicketCreateSerializer
            return TicketCreateSerializer
        return TicketSerializer

class TicketDetailView(BaseWorkItemDetailView):
    model = Ticket
    allowed_type = WorkItemType.TICKET

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TicketWritableSerializer
        return TicketSerializer
    serializer_class = TicketSerializer


class CaseListView(BaseWorkItemListView):
    model = Case
    serializer_class = CaseSerializer
    allowed_type = WorkItemType.CASE
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class CaseDetailView(BaseWorkItemDetailView):
    model = Case
    serializer_class = CaseSerializer
    allowed_type = WorkItemType.CASE


class JobListView(BaseWorkItemListView):
    model = Job
    serializer_class = JobSerializer
    allowed_type = WorkItemType.JOB
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class JobDetailView(BaseWorkItemDetailView):
    model = Job
    serializer_class = JobSerializer
    allowed_type = WorkItemType.JOB

