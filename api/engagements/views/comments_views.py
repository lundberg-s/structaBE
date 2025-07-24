from rest_framework import generics, permissions

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend

from engagements.models import Comment, ActivityLog
from engagements.serializers.comment_serializers import (
    CommentSerializer,
    CommentListSerializer,
)
from core.views.base_views import BaseView


class CommentListView(BaseView, ListCreateAPIView):
    queryset = Comment.objects.select_related("created_by", "work_item").all()
    serializer_class = CommentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["work_item", "created_by"]
    search_fields = ["content"]

    def get_queryset(self):
        base_queryset = self.get_tenant_queryset(Comment)
        return self.serializer_class.get_optimized_queryset(base_queryset)

    def perform_create(self, serializer):
        # Only allow work_item from user's tenant
        work_item = serializer.validated_data.get("work_item")
        if work_item.tenant != self.get_tenant():
            raise PermissionDenied("Invalid work item for this tenant.")
        instance = serializer.save(
            tenant=self.get_tenant(), created_by=self.get_user()
        )
        self.log_activity(
            instance, 
            "commented", 
            "commented on", 
            work_item=work_item
        )


class CommentDetailView(BaseView, RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        # Only allow access to comments from user's tenant
        base_queryset = self.get_tenant_queryset(Comment)
        return self.serializer_class.get_optimized_queryset(base_queryset)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.log_activity(
            instance, 
            "updated", 
            "updated comment on", 
            work_item=instance.work_item
        )

    def perform_destroy(self, instance):
        self.log_activity(
            instance, 
            "deleted", 
            "deleted comment from", 
            work_item=instance.work_item
        )
        instance.delete()
