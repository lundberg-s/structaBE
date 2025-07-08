from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from workflow.models import WorkItemPartnerRole
from workflow.serializers.partner_role_serializers import WorkItemPartnerRoleCreateSerializer, WorkItemPartnerRoleGetSerializer

class WorkItemPartnerRoleListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkItemPartnerRole.objects.filter(tenant=self.request.user.tenant)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkItemPartnerRoleCreateSerializer
        return WorkItemPartnerRoleGetSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

class WorkItemPartnerRoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkItemPartnerRole.objects.filter(tenant=self.request.user.tenant)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WorkItemPartnerRoleCreateSerializer
        return WorkItemPartnerRoleGetSerializer 