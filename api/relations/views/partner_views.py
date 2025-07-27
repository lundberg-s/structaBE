from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from relations.models import Partner
from core.models import Role
from relations.choices import SystemRole

from core.views.base_views import BaseView

class PartnerListView(BaseView, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def get_queryset(self):
        return self.get_tenant_queryset(Partner)

    def perform_create(self, serializer):
        partner = serializer.save(tenant=self.get_tenant())
        # Note: Role assignment is now handled directly on the Partner model


class PartnerDetailView(BaseView, RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.get_tenant_queryset(Partner)