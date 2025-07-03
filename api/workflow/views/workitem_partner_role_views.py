from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from workflow.models import WorkItemPartnerRole
from user.models import Partner
from user.serializers import PartnerSerializer
from workflow.serializers import WorkItemPartnerRoleSerializer

class WorkItemPartnerRoleViewSet(viewsets.ModelViewSet):
    serializer_class = WorkItemPartnerRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkItemPartnerRole.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant) 