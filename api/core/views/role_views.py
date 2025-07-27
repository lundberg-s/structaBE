from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.models import Role
from core.serializers.role_serializers import RoleSerializer

class RoleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save()

class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant) 