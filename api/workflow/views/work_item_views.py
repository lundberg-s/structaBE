from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from workflow.serializers import TicketSerializer, JobSerializer, CaseSerializer, WorkItemSerializer, TicketWritableSerializer
from workflow.models import Ticket, Job, Case, WorkItem

from user.models import WorkItemType
from workflow.models import Assignment
from workflow.serializers import AssignmentSerializer
from rest_framework import generics

class BaseWorkItemListView(ListCreateAPIView):
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
    permission_classes = [IsAuthenticated]
    allowed_type = None

    def get_queryset(self):
        if self.request.user.tenant.work_item_type.lower() != self.allowed_type:
            return self.model.objects.none()
        return self.model.objects.filter(tenant=self.request.user.tenant)

    def perform_update(self, serializer):
        if self.request.user.tenant.work_item_type.lower() == self.allowed_type:
            serializer.save(tenant=self.request.user.tenant)



class TicketWorkItemListView(BaseWorkItemListView):
    model = Ticket
    serializer_class = TicketSerializer
    allowed_type = WorkItemType.TICKET
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class TicketWorkItemDetailView(BaseWorkItemDetailView):
    model = Ticket
    serializer_class = TicketSerializer
    allowed_type = WorkItemType.TICKET
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            from workflow.serializers import TicketWritableSerializer
            return TicketWritableSerializer
        from workflow.serializers import TicketSerializer
        return TicketSerializer


class CaseWorkItemListView(BaseWorkItemListView):
    model = Case
    serializer_class = CaseSerializer
    allowed_type = WorkItemType.CASE
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class CaseWorkItemDetailView(BaseWorkItemDetailView):
    model = Case
    serializer_class = CaseSerializer
    allowed_type = WorkItemType.CASE


class JobWorkItemListView(BaseWorkItemListView):
    model = Job
    serializer_class = JobSerializer
    allowed_type = WorkItemType.JOB
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

class JobWorkItemDetailView(BaseWorkItemDetailView):
    model = Job
    serializer_class = JobSerializer
    allowed_type = WorkItemType.JOB


class AssignmentCreateView(generics.CreateAPIView):
    queryset = Assignment.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            from workflow.serializers import AssignmentCreateSerializer
            return AssignmentCreateSerializer
        from workflow.serializers import AssignmentSerializer
        return AssignmentSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

