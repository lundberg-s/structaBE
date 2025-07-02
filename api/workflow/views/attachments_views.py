from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter

from django_filters.rest_framework import DjangoFilterBackend

from workflow.models import Attachment, ActivityLog
from workflow.serializers import AttachmentSerializer

class AttachmentListCreateView(generics.ListCreateAPIView):
    queryset = Attachment.objects.select_related('uploaded_by', 'workitem').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['workitem', 'mime_type', 'uploaded_by']
    search_fields = ['filename']

    def get_queryset(self):
        return Attachment.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, uploaded_by=self.request.user)
        ActivityLog.objects.create(
            workitem=serializer.instance.workitem,
            user=self.request.user,
            activity_type='attachment_added',
            description=f'Attachment "{serializer.instance.filename}" was added'
        )

class AttachmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.select_related('uploaded_by', 'workitem').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        attachment = serializer.save()
        ActivityLog.objects.create(
            workitem=attachment.workitem,
            user=self.request.user,
            activity_type='attachment_updated',
            description=f'Attachment "{attachment.filename}" was updated'
        )

    def perform_destroy(self, instance):
        ActivityLog.objects.create(
            workitem=instance.workitem,
            user=self.request.user,
            activity_type='attachment_deleted',
            description=f'Attachment "{instance.filename}" was deleted'
        )
        instance.delete()