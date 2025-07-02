from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from diarium.models import WorkItemPartyRole
from user.models import Party
from user.serializers import PartySerializer
from diarium.serializers import WorkItemPartyRoleSerializer

class WorkItemPartyRoleViewSet(viewsets.ModelViewSet):
    serializer_class = WorkItemPartyRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkItemPartyRole.objects.filter(tenant=self.request.user.party.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.party.tenant) 