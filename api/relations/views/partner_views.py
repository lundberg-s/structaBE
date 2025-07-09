from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from relations.models import Partner, Role, PartnerRoleTypes



class PartnerListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return Partner.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)
        Role.objects.create(
            partner=serializer.instance,
            role_type=PartnerRoleTypes.CONTACT_INFO,
            tenant=self.request.user.tenant
        )


class PartnerDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Partner.objects.filter(tenant=self.request.user.tenant)