from rest_framework import permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import Attachment, ActivityLog
from engagements.serializers.attachment_serializers import AttachmentSerializer

class AttachmentListView(ListCreateAPIView):
    queryset = Attachment.objects.select_related('created_by', 'work_item').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['work_item', 'mime_type', 'created_by']
    search_fields = ['filename']

    def get_queryset(self):
        return Attachment.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        work_item = serializer.validated_data.get('work_item')
        if work_item.tenant != self.request.user.tenant:
            raise PermissionDenied('Invalid work item for this tenant.')
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=serializer.instance.work_item,
            created_by=self.request.user,
            activity_type='attachment_added',
            description=f'Attachment "{serializer.instance.filename}" was added'
        )

class AttachmentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Attachment.objects.filter(tenant=self.request.user.tenant)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # Only uploader can update/delete
        if request.method in ['PUT', 'PATCH', 'DELETE'] and obj.created_by != request.user:
            raise PermissionDenied('You do not have permission to modify this attachment.')

    def perform_update(self, serializer):
        attachment = serializer.save()
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=attachment.work_item,
            created_by=self.request.user,
            activity_type='attachment_updated',
            description=f'Attachment "{attachment.filename}" was updated'
        )

    def perform_destroy(self, instance):
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=instance.work_item,
            created_by=self.request.user,
            activity_type='attachment_deleted',
            description=f'Attachment "{instance.filename}" was deleted'
        )
        instance.delete()