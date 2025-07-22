from rest_framework import serializers
from engagements.models import WorkItem
from django.contrib.auth import get_user_model
from users.serializers.user_serializers import UserWithPersonSerializer

from engagements.serializers.attachment_serializers import AttachmentSerializer
from engagements.serializers.comment_serializers import CommentSerializer
from engagements.serializers.activity_log_serializers import ActivityLogSerializer
from engagements.serializers.partner_role_serializers import FlatPartnerWithRoleSerializer
from engagements.utilities.assignment_utilities import update_work_item_assignments

User = get_user_model()

class WorkItemListSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'tenant', 'created_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at'] 

class WorkItemSerializer(serializers.ModelSerializer):
    assigned_to = UserWithPersonSerializer(many=True, read_only=True)
    created_by = UserWithPersonSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    activity_log = ActivityLogSerializer(many=True, read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_to', 'created_by', 'attachments',
            'comments', 'activity_log', 'created_at', 'updated_at', 'tenant'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant']

    def get_assigned_to(self, obj):
        # Use the prefetched data directly without creating new serializers
        if hasattr(obj, '_prefetched_objects_cache') and 'assignments' in obj._prefetched_objects_cache:
            return [
                {
                    'id': str(a.user.id),
                    'username': a.user.username,
                    'email': a.user.email,
                    'first_name': a.user.partner.person.first_name if hasattr(a.user, 'partner') and a.user.partner and hasattr(a.user.partner, 'person') else '',
                    'last_name': a.user.partner.person.last_name if hasattr(a.user, 'partner') and a.user.partner and hasattr(a.user.partner, 'person') else ''
                }
                for a in obj.assignments.all()
            ]
        # Fallback for when prefetch is not available
        return [UserWithPersonSerializer(a.user).data for a in obj.assignments.select_related('user__partner__person').all()]

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
    assigned_to = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = WorkItem
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_to'
        ]

    def update(self, instance, validated_data):
        assigned_to_ids = validated_data.pop('assigned_to', None)

        # Standard update
        instance = super().update(instance, validated_data)

        if assigned_to_ids is not None:
            update_work_item_assignments(
                work_item=instance,
                new_user_ids=assigned_to_ids,
                assigned_by_user=self.context['request'].user
            )

        return instance
