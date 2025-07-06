from rest_framework import serializers
from workflow.models import WorkItem, Ticket, Case, Job, Attachment, Comment, ActivityLog, WorkItemPartnerRole
from django.contrib.auth import get_user_model
from user.models import Tenant, Partner, Organization, Person
from user.serializers import PartnerSerializer, OrganizationSerializer, PersonSerializer, FlatOrganizationSerializer, FlatPersonSerializer
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from workflow.utilities import get_partner_content_type_and_obj

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
    
    def _get_partner_person_field(self, obj, field_name):
        if hasattr(obj, 'partner') and obj.partner and hasattr(obj.partner, 'person'):
            return getattr(obj.partner.person, field_name)
        return getattr(obj, field_name) or ''
    
    def get_first_name(self, obj):
        return self._get_partner_person_field(obj, 'first_name')
    
    def get_last_name(self, obj):
        return self._get_partner_person_field(obj, 'last_name')

class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Attachment
        fields = ['id', 'work_item', 'file', 'filename', 'file_size', 'mime_type', 'uploaded_by', 'uploaded_at', 'tenant']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'tenant']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'work_item', 'content', 'author', 'created_at', 'updated_at', 'tenant']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'tenant']
        
class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ActivityLog
        fields = ['id', 'work_item', 'activity_type', 'description', 'user', 'created_at', 'tenant']
        read_only_fields = ['id', 'user', 'created_at', 'tenant']

class WorkItemPartnerRoleNestedSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)
    class Meta:
        model = WorkItemPartnerRole
        fields = ['id', 'partner']

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

class FlatPartnerWithRoleSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        partner = obj.partner
        if partner is None:
            return None
        if isinstance(partner, Organization):
            data = dict(FlatOrganizationSerializer(partner).data)
            data['role'] = obj.role
            data['content_type'] = obj.content_type.model
            return {
                'organization': data
            }
        elif isinstance(partner, Person):
            data = dict(FlatPersonSerializer(partner).data)
            data['role'] = obj.role
            data['content_type'] = obj.content_type.model
            return {
                'person': data
            }
        else:
            data = {}
            data['role'] = obj.role
            data['content_type'] = obj.content_type.model if obj.content_type else None
            return {
                'unknown': data
            }

class WorkItemSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    activity_log = ActivityLogSerializer(many=True, read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    partner_roles = FlatPartnerWithRoleSerializer(many=True, read_only=True)
    class Meta:
        model = WorkItem
        fields = [
            'id', 'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user', 'created_by', 'attachments',
            'comments', 'activity_log', 'partner_roles', 'created_at', 'updated_at', 'tenant'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant']

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

class WorkItemPartnerRoleCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.filter(model__in=['person', 'organization']),
        slug_field='model'
    )
    object_id = serializers.UUIDField()

    class Meta:
        model = WorkItemPartnerRole
        fields = ['work_item', 'content_type', 'object_id', 'role']

    def validate(self, attrs):
        content_type = attrs.get('content_type')
        object_id = attrs.get('object_id')
        model_class = content_type.model_class()
        if not model_class.objects.filter(id=object_id).exists():
            raise ValidationError({'object_id': 'No matching object found for this content type.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('partner_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('partner_id', None)
        return super().update(instance, validated_data)

class WorkItemPartnerRoleGetSerializer(serializers.ModelSerializer):
    partner = serializers.SerializerMethodField()

    class Meta:
        model = WorkItemPartnerRole
        fields = ['id', 'partner', 'role', 'tenant']

    def get_partner(self, obj):
        partner = obj.partner
        if isinstance(partner, Organization):
            return OrganizationSerializer(partner).data
        elif isinstance(partner, Person):
            return PersonSerializer(partner).data
        return None 