from rest_framework import serializers
from engagements.models import WorkItem
from users.serializers.user_serializers import UserWithPersonSerializer

from engagements.serializers.attachment_serializers import AttachmentSerializer
from engagements.serializers.comment_serializers import CommentSerializer
from engagements.serializers.activity_log_serializers import ActivityLogSerializer


class WorkItemListSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = UserWithPersonSerializer(read_only=True)

    class Meta:
        model = WorkItem
        fields = [
            "id",
            "title",
            "status",
            "category",
            "priority",
            "deadline",
            "tenant",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "tenant", "created_at", "created_by"]

    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for ticket list serialization."""
        if queryset is None:
            queryset = WorkItem.objects.all()
        
        return queryset.select_related(
            'created_by__partner__person',
            'tenant'
        )


class WorkItemSerializer(serializers.ModelSerializer):
    # REMOVED: assigned_to = UserWithPersonSerializer(many=True, read_only=True)
    created_by = UserWithPersonSerializer(read_only=True)
    # attachments = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    # activity_log = ActivityLogSerializer(many=True, read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkItem
        fields = [
            "id",
            "title",
            "description",
            "status",
            "category",
            "priority",
            "deadline",
            "created_by",
            # "attachments",
            "comments",
            # "activity_log",
            "created_at",
            "updated_at",
            "tenant",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "tenant"]
        
    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for ticket detail serialization."""
        if queryset is None:
            queryset = WorkItem.objects.all()
        
        return queryset.select_related(
            'created_by__partner__person',
            'tenant'
        ).prefetch_related(
            'comments__author__partner__person',
            # 'attachments__uploaded_by__partner__person',
            # 'activity_log__user__partner__person',
        )

class WorkItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = ["title", "description", "status", "category", "priority", "deadline"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "tenant"]


class WorkItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = ["title", "description", "status", "category", "priority", "deadline"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "tenant"]


class WorkItemDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = ["id"]
        read_only_fields = ["id"]
