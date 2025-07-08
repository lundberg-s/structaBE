from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter

from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import Comment
from engagements.serializers.comment_serializers import CommentSerializer

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.select_related('author', 'work_item').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['work_item', 'author']
    search_fields = ['content']

    def get_queryset(self):
        return Comment.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.tenant,
            author=self.request.user
        )

class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('author', 'work_item').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id' 