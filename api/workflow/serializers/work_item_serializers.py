from rest_framework import serializers
from workflow.models import WorkItem
from django.contrib.auth import get_user_model
from user.serializers.user_serializers import UserWithPersonSerializer

from workflow.serializers.attachment_serializers import AttachmentSerializer
from workflow.serializers.comment_serializers import CommentSerializer
from workflow.serializers.activity_log_serializers import ActivityLogSerializer
from workflow.serializers.partner_role_serializers import FlatPartnerWithRoleSerializer

User = get_user_model()

class WorkItemSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()
    created_by = UserWithPersonSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    activity_log = ActivityLogSerializer(many=True, read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    partner_roles = FlatPartnerWithRoleSerializer(many=True, read_only=True)
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_to', 'created_by', 'attachments',
            'comments', 'activity_log', 'partner_roles', 'created_at', 'updated_at', 'tenant'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant']

    def get_assigned_to(self, obj):
        return [UserWithPersonSerializer(a.user).data for a in obj.assignments.all()]

class WorkItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline'
        ]

class WorkItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline'
        ]

class WorkItemWritableSerializer(serializers.ModelSerializer):
    assigned_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = WorkItem
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user'
        ]

class WorkItemListSerializer(serializers.ModelSerializer):
    assigned_user = UserWithPersonSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'assigned_user', 'tenant',
        ]
        read_only_fields = ['id', 'tenant'] 