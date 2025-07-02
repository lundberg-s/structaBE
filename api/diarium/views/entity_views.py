from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from diarium.models import Customer, Organization, Vendor
from diarium.serializers import EntitySerializer

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(tenant=self.request.user.tenant)  # type: ignore

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(tenant=self.request.user.tenant)  # type: ignore

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vendor.objects.filter(tenant=self.request.user.tenant)  # type: ignore

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant) 