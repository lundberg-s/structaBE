from rest_framework import serializers
from engagements.models import WorkItemStatus


class WorkItemStatusSerializer(serializers.ModelSerializer):
    """Serializer for work item status options."""
    
    class Meta:
        model = WorkItemStatus
        fields = [
            'id', 'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkItemStatusListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing work item status options."""
    
    class Meta:
        model = WorkItemStatus
        fields = ['id', 'label', 'translated_label', 'use_translation', 'color', 'is_active']


class WorkItemStatusCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating work item status options."""
    
    class Meta:
        model = WorkItemStatus
        fields = [
            'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active'
        ]


class WorkItemStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating work item status options."""
    
    class Meta:
        model = WorkItemStatus
        fields = [
            'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active'
        ] 