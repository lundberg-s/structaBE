from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter

from django_filters.rest_framework import DjangoFilterBackend

from diarium.models import Attachment, ActivityLog
from diarium.serializers import AttachmentSerializer

class AttachmentListCreateView(generics.ListCreateAPIView):
    queryset = Attachment.objects.select_related('uploaded_by', 'case').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['case', 'mime_type', 'uploaded_by']
    search_fields = ['filename']

    def perform_create(self, serializer):
        attachment = serializer.save(uploaded_by=self.request.user)
        ActivityLog.objects.create(
            case=attachment.case,
            user=self.request.user,
            activity_type='attachment_added',
            description=f'Attachment "{attachment.filename}" was added'
        )

class AttachmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.select_related('uploaded_by', 'case').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        attachment = serializer.save()
        ActivityLog.objects.create(
            case=attachment.case,
            user=self.request.user,
            activity_type='attachment_updated',
            description=f'Attachment "{attachment.filename}" was updated'
        )

    def perform_destroy(self, instance):
        ActivityLog.objects.create(
            case=instance.case,
            user=self.request.user,
            activity_type='attachment_deleted',
            description=f'Attachment "{instance.filename}" was deleted'
        )
        instance.delete()