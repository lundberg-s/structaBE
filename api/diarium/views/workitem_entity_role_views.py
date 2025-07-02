from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from diarium.models import WorkItemEntityRole
from diarium.serializers import WorkItemEntityRoleSerializer

class WorkItemEntityRoleViewSet(viewsets.ModelViewSet):
    serializer_class = WorkItemEntityRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkItemEntityRole.objects.filter(tenant=self.request.user.tenant)  # type: ignore

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant) 