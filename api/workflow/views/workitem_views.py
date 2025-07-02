from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from workflow.models import WorkItem, Ticket, Job, Case
from workflow.serializers import WorkItemSerializer, WorkItemCreateSerializer, WorkItemUpdateSerializer, TicketSerializer, JobSerializer, CaseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404


serializer_map = {
    'ticket': TicketSerializer,
    'job': JobSerializer,
    'case': CaseSerializer,
}
model_map = {
    'ticket': Ticket,
    'job': Job,
    'case': Case,
}
filterset_fields_map = {
    'ticket': ['status', 'priority', 'assigned_user'],
    'job': ['status', 'priority', 'assigned_user'],
    'case': ['status', 'priority', 'assigned_user'],
}
search_fields_map = {
    'ticket': ['title', 'description'],
    'job': ['title', 'description'],
    'case': ['title', 'description'],
}

class CurrentWorkItemListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        return WorkItem.objects.filter(tenant=self.request.user.party.tenant)

    def get_serializer_class(self):
        tenant = self.request.user.tenant
        workitem_type = tenant.workitem_type
        return serializer_map.get(workitem_type)

    @property
    def filterset_fields(self):
        tenant = self.request.user.tenant
        workitem_type = tenant.workitem_type
        return filterset_fields_map.get(workitem_type, [])

    @property
    def search_fields(self):
        tenant = self.request.user.tenant
        workitem_type = tenant.workitem_type
        return search_fields_map.get(workitem_type, [])

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.party.tenant)

class CurrentWorkItemDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        tenant = self.request.user.tenant
        workitem_type = tenant.workitem_type
        model = model_map.get(workitem_type)
        if not model:
            from workflow.models import Ticket
            return Ticket.objects.none()
        return model.objects.filter(tenant=tenant)

    def get_serializer_class(self):
        tenant = self.request.user.tenant
        workitem_type = tenant.workitem_type
        return serializer_map.get(workitem_type) 