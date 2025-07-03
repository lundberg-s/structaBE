from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from user.models import Person, Organization, Party
from user.serializers import (
    PersonSerializer, OrganizationSerializer
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class PartyListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return Party.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class PartyDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Party.objects.filter(tenant=self.request.user.tenant)


class PersonListView(PartyListView):
    model = Person
    serializer_class = PersonSerializer
    filterset_fields = ['first_name', 'last_name', 'email', 'phone']

class PersonDetailView(PartyDetailView):
    model = Person
    serializer_class = PersonSerializer
    filterset_fields = ['first_name', 'last_name', 'email', 'phone']

class OrganizationListView(PartyListView):
    model = Organization
    serializer_class = OrganizationSerializer
    filterset_fields = ['name', 'organization_number']

class OrganizationDetailView(PartyDetailView):
    model = Organization
    serializer_class = OrganizationSerializer
    filterset_fields = ['name', 'organization_number']