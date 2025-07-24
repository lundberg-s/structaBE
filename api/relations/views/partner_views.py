from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from relations.models import Partner, Role
from relations.choices import SystemRole
from relations.tests.factory import create_relation_reference_for_person, create_relation_reference_for_organization
from core.views.base_views import BaseView

class PartnerListView(BaseView, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return self.get_tenant_queryset(Partner)

    def perform_create(self, serializer):
        partner = serializer.save(tenant=self.get_tenant())
        # Create RelationReference for the partner
        if hasattr(partner, 'person'):
            ref = create_relation_reference_for_person(partner)
        elif hasattr(partner, 'organization'):
            ref = create_relation_reference_for_organization(partner)
        else:
            return  # Should not happen
        
        # Create a role for the partner
        Role.objects.create(
            tenant=self.get_tenant(),
            target=ref,
            system_role=SystemRole.CONTACT_INFO
        )


class PartnerDetailView(BaseView, RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.get_tenant_queryset(Partner)