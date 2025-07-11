from rest_framework import generics, permissions

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import Comment, ActivityLog
from engagements.serializers.comment_serializers import CommentSerializer

class CommentListView(ListCreateAPIView):
    queryset = Comment.objects.select_related('author', 'work_item').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['work_item', 'author']
    search_fields = ['content']

    def get_queryset(self):
        return Comment.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        # Only allow work_item from user's tenant
        work_item = serializer.validated_data.get('work_item')
        if work_item.tenant != self.request.user.tenant:
            raise PermissionDenied('Invalid work item for this tenant.')
        instance = serializer.save(
            tenant=self.request.user.tenant,
            author=self.request.user
        )
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=work_item,
            user=self.request.user,
            activity_type='commented',
            description=f'Comment added to "{work_item.title}".'
        )

class CommentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Only allow access to comments from user's tenant
        return Comment.objects.filter(tenant=self.request.user.tenant)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # Only author can update/delete
        if request.method in ['PUT', 'PATCH', 'DELETE'] and obj.author != request.user:
            raise PermissionDenied('You do not have permission to modify this comment.')

    def perform_update(self, serializer):
        instance = serializer.save()
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=instance.work_item,
            user=self.request.user,
            activity_type='updated',
            description=f'Comment updated on "{instance.work_item.title}".'
        )
    def perform_destroy(self, instance):
        ActivityLog.objects.create(
            tenant=self.request.user.tenant,
            work_item=instance.work_item,
            user=self.request.user,
            activity_type='deleted',
            description=f'Comment deleted from "{instance.work_item.title}".'
        )
        instance.delete() 