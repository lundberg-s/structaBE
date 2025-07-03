from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from user.models import Person, Organization, Partner
from user.serializers import (
    PersonSerializer, OrganizationSerializer
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class PartnerListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return Partner.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class PartnerDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Partner.objects.filter(tenant=self.request.user.tenant)


class PersonListView(PartnerListView):
    model = Person
    serializer_class = PersonSerializer
    filterset_fields = ['first_name', 'last_name', 'email', 'phone']

class PersonDetailView(PartnerDetailView):
    model = Person
    serializer_class = PersonSerializer
    filterset_fields = ['first_name', 'last_name', 'email', 'phone']

class OrganizationListView(PartnerListView):
    model = Organization
    serializer_class = OrganizationSerializer
    filterset_fields = ['name', 'organization_number']

class OrganizationDetailView(PartnerDetailView):
    model = Organization
    serializer_class = OrganizationSerializer
    filterset_fields = ['name', 'organization_number']