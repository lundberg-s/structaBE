from rest_framework import serializers
from engagements.models import WorkItemCategory


class WorkItemCategorySerializer(serializers.ModelSerializer):
    """Serializer for work item category options."""
    
    class Meta:
        model = WorkItemCategory
        fields = [
            'id', 'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkItemCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing work item category options."""
    
    class Meta:
        model = WorkItemCategory
        fields = ['id', 'label', 'translated_label', 'use_translation', 'color', 'is_active']


class WorkItemCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating work item category options."""
    
    class Meta:
        model = WorkItemCategory
        fields = [
            'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active'
        ]


class WorkItemCategoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating work item category options."""
    
    class Meta:
        model = WorkItemCategory
        fields = [
            'label', 'translated_label', 'use_translation', 
            'color', 'sort_order', 'is_active'
        ] 