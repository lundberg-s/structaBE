from rest_framework import serializers
from engagements.models import WorkItemPriority


class WorkItemPrioritySerializer(serializers.ModelSerializer):
    """Serializer for work item priority options."""
    
    class Meta:
        model = WorkItemPriority
        fields = [
            'id', 'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkItemPriorityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing work item priority options."""
    
    class Meta:
        model = WorkItemPriority
        fields = ['id', 'label', 'translated_label', 'use_translation', 'color', 'is_active']


class WorkItemPriorityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating work item priority options."""
    
    class Meta:
        model = WorkItemPriority
        fields = [
            'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active'
        ]


class WorkItemPriorityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating work item priority options."""
    
    class Meta:
        model = WorkItemPriority
        fields = [
            'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active'
        ] 