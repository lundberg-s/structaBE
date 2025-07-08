from user.models import Organization  

from user.serializers.organization_serializers import OrganizationSerializer

from user.views.partner_views import PartnerListView, PartnerDetailView

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