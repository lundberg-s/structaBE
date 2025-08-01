from rest_framework import serializers
from core.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model.
    Provides read-only access to audit trail data.
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'entity_type', 'entity_id', 'entity_name',
            'activity_type', 'description', 'change_summary',
            'old_values', 'new_values', 'session_id', 'ip_address',
            'user_agent', 'business_process', 'transaction_id',
            'compliance_category', 'risk_level', 'created_by',
            'created_by_username', 'created_by_email', 'created_at'
        ]
        read_only_fields = fields  # All fields are read-only for audit logs 