from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import Attachment
from engagements.serializers.attachment_serializers import AttachmentSerializer
from core.views.base_views import BaseView

class AttachmentListView(BaseView, ListCreateAPIView):
    queryset = Attachment.objects.select_related('work_item').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['work_item', 'mime_type', 'created_by']
    search_fields = ['filename']

    def get_queryset(self):
        return self.get_tenant_queryset(Attachment)

    def perform_create(self, serializer):
        work_item = serializer.validated_data.get('work_item')
        if work_item.tenant != self.get_tenant():
            raise PermissionDenied('Invalid work item for this tenant.')
        instance = serializer.save(tenant=self.get_tenant(), created_by=self.get_user().id)
        self.log_activity(instance, 'created', 'created')

class AttachmentDetailView(BaseView, RetrieveUpdateDestroyAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_tenant_queryset(Attachment)

    def perform_update(self, serializer):
        attachment = serializer.save()
        self.log_activity(attachment, 'updated', 'updated')

    def perform_destroy(self, instance):
        self.log_activity(instance, 'deleted', 'deleted')
        instance.delete()