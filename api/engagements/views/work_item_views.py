from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from engagements.serializers.ticket_serializers import TicketSerializer, TicketWritableSerializer
from engagements.serializers.job_serializers import JobSerializer
from engagements.serializers.case_serializers import CaseSerializer

from engagements.models import Ticket, Job, Case, WorkItem

from core.models import WorkItemType


class BaseWorkItemListView(ListCreateAPIView):
    model = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    allowed_type = None

    def get_queryset(self):
        if self.request.user.tenant.work_item_type.lower() != self.allowed_type:
            return self.model.objects.none()
        return self.model.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        if self.request.user.tenant.work_item_type.lower() == self.allowed_type:
            serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


class BaseWorkItemDetailView(RetrieveUpdateDestroyAPIView):
    model = None
    permission_classes = [IsAuthenticated]
    allowed_type = None

    def get_queryset(self):
        if self.request.user.tenant.work_item_type.lower() != self.allowed_type:
            return self.model.objects.none()
        return self.model.objects.filter(tenant=self.request.user.tenant)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # Only creator can update/delete
        if request.method in ['PUT', 'PATCH', 'DELETE'] and hasattr(obj, 'created_by') and obj.created_by != request.user:
            raise PermissionDenied('You do not have permission to modify this resource.')

    def perform_update(self, serializer):
        if self.request.user.tenant.work_item_type.lower() == self.allowed_type:
            serializer.save(tenant=self.request.user.tenant)



class TicketListView(BaseWorkItemListView):
    model = Ticket
    serializer_class = TicketSerializer
    allowed_type = WorkItemType.TICKET
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

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

