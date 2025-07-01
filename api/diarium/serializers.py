from rest_framework import serializers
from diarium.models import Case, Attachment, Comment, ActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Attachment
        fields = ['id', 'case', 'file', 'filename', 'file_size', 'mime_type', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'case', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'case', 'activity_type', 'description', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class CaseListSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'status', 'category', 'priority',
            'deadline', 'assigned_user',
        ]
        read_only_fields = ['id']

class CaseSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    attachments = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    activity_log = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            'id', 'title', 'description', 'status', 'category', 'priority',
            'deadline', 'assigned_user', 'created_by', 'attachments',
            'comments', 'activity_log', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_attachments(self, obj):
        qs = obj.attachments.all().order_by('-uploaded_at')[:5]
        return AttachmentSerializer(qs, many=True).data

    def get_activity_log(self, obj):
        qs = obj.activity_log.all().order_by('-created_at')[:5]
        return ActivityLogSerializer(qs, many=True).data

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