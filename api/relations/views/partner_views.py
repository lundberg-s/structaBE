from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from relations.models import Partner, Role
from relations.choices import SystemRole
from relations.tests.factory import create_relation_reference_for_person, create_relation_reference_for_organization

class PartnerListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return Partner.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        partner = serializer.save(tenant=self.request.user.tenant)
        # Create RelationReference for the partner
        if hasattr(partner, 'person'):
            ref = create_relation_reference_for_person(partner)
        elif hasattr(partner, 'organization'):
            ref = create_relation_reference_for_organization(partner)
        else:
            return  # Should not happen
        
        # Create a role for the partner
        Role.objects.create(
            tenant=self.request.user.tenant,
            target=ref,
            system_role=SystemRole.CONTACT_INFO
        )


class PartnerDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Partner.objects.filter(tenant=self.request.user.tenant)