from rest_framework.generics import RetrieveUpdateDestroyAPIView
from partners.models import Organization  

from partners.serializers import OrganizationSerializer

from partners.views import PartnerListView, PartnerDetailView

class OrganizationListView(PartnerListView):
    model = Organization
    serializer_class = OrganizationSerializer
    
    def get_queryset(self):
        return Organization.objects.filter(tenant=self.request.user.tenant)

class OrganizationDetailView(PartnerDetailView):
    model = Organization
    serializer_class = OrganizationSerializer
    
    def get_queryset(self):
        return Organization.objects.filter(tenant=self.request.user.tenant)