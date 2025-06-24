from rest_framework import generics, permissions
from diarium.models import Attachment
from diarium.serializers import AttachmentSerializer

class AttachmentListCreateView(generics.ListCreateAPIView):
    queryset = Attachment.objects.select_related('uploaded_by', 'case').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class AttachmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attachment.objects.select_related('uploaded_by', 'case').all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 