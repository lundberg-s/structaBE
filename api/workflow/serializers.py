from rest_framework import serializers
from workflow.models import WorkItem, Ticket, Case, Job, Attachment, Comment, ActivityLog, WorkItemPartyRole
from django.contrib.auth import get_user_model
from user.models import Tenant, Party, Organization
from user.serializers import PartySerializer
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class WorkItemPartyRoleSerializer(serializers.ModelSerializer):
    party = PartySerializer(read_only=True)
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.filter(model__in=['person', 'organization']),
        slug_field='model',
        write_only=True
    )
    object_id = serializers.UUIDField(write_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkItemPartyRole
        fields = ['id', 'workitem', 'party', 'content_type', 'object_id', 'role', 'tenant']
        read_only_fields = ['id', 'party', 'tenant']

    def create(self, validated_data):
        content_type_model = validated_data.pop('content_type')
        content_type = ContentType.objects.get(model=content_type_model)
        validated_data['content_type'] = content_type
        return super().create(validated_data)

class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Attachment
        fields = ['id', 'workitem', 'file', 'filename', 'file_size', 'mime_type', 'uploaded_by', 'uploaded_at', 'tenant']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'tenant']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'workitem', 'content', 'author', 'created_at', 'updated_at', 'tenant']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'tenant']

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ActivityLog
        fields = ['id', 'workitem', 'activity_type', 'description', 'user', 'created_at', 'tenant']
        read_only_fields = ['id', 'user', 'created_at', 'tenant']

class WorkItemPartyRoleNestedSerializer(serializers.ModelSerializer):
    party = PartySerializer(read_only=True)
    class Meta:
        model = WorkItemPartyRole
        fields = ['id', 'party', 'role']

class WorkItemListSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'assigned_user', 'tenant',
        ]
        read_only_fields = ['id', 'tenant']

class WorkItemSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    activity_log = ActivityLogSerializer(many=True, read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    party_roles = WorkItemPartyRoleNestedSerializer(many=True, read_only=True)
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user', 'created_by', 'attachments',
            'comments', 'activity_log', 'party_roles', 'created_at', 'updated_at', 'tenant'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Dynamically add only roles that have entities
        for role_obj in instance.party_roles.all():
            role = role_obj.role
            party_data = WorkItemPartyRoleNestedSerializer(role_obj.party).data
            if role in data:
                data[role].append(party_data)
            else:
                data[role] = [party_data]
        return data

class WorkItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user'
        ]

class WorkItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItem
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user'
        ]

# Ticket, Case, Job serializers with their specific fields
class TicketSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Ticket
        fields = WorkItemSerializer.Meta.fields + ['ticket_number', 'reported_by', 'urgency']

class CaseSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Case
        fields = WorkItemSerializer.Meta.fields + ['case_reference', 'legal_area', 'court_date']

class JobSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Job
        fields = WorkItemSerializer.Meta.fields + ['job_code', 'assigned_team', 'estimated_hours']

class CaseListSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'assigned_user',
        ]
        read_only_fields = ['id']

class CaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user'
        ]

class CaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user'
        ]

class ActiveCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'assigned_user',
        ]
        read_only_fields = ['id']

class LongestOpenCaseSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField()
    status = serializers.CharField()
    assigned_user = serializers.CharField(allow_null=True)

class CaseStatisticsSerializer(serializers.Serializer):
    total_cases = serializers.IntegerField()
    cases_by_status = serializers.DictField(child=serializers.IntegerField())
    cases_by_priority = serializers.DictField(child=serializers.IntegerField())
    cases_by_category = serializers.DictField(child=serializers.IntegerField())
    cases_created_per_month = serializers.DictField(child=serializers.IntegerField())
    cases_resolved_per_month = serializers.DictField(child=serializers.IntegerField())
    cases_created_per_week = serializers.DictField(child=serializers.IntegerField())
    cases_resolved_per_week = serializers.DictField(child=serializers.IntegerField())
    open_cases_at_month_end = serializers.DictField(child=serializers.IntegerField())
    avg_cases_per_user = serializers.FloatField()
    cases_resolved_per_user = serializers.DictField(child=serializers.IntegerField())
    unassigned_cases = serializers.IntegerField()
    avg_time_to_first_response_hours = serializers.FloatField(allow_null=True)
    avg_time_in_status_hours = serializers.DictField(child=serializers.FloatField())
    cases_reopened = serializers.IntegerField()
    overdue_cases = serializers.IntegerField()
    longest_open_cases = LongestOpenCaseSerializer(many=True)
    sla_compliance_percent = serializers.FloatField(allow_null=True)
    average_resolution_time_days = serializers.FloatField(allow_null=True)
    cases_by_assigned_user = serializers.DictField(child=serializers.IntegerField())
    cases_by_created_user = serializers.DictField(child=serializers.IntegerField()) 