from rest_framework import serializers
from engagements.models import Comment
from users.mixins import CreatedByUserMixin


class CommentListSerializer(CreatedByUserMixin, serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'work_item', 'content', 'created_by', 'created_at', 'updated_at', 'tenant']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant'] 

    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for comment serialization."""
        if queryset is None:
            queryset = Comment.objects.all()
        
        # Use the mixin's optimized queryset
        queryset = super().get_optimized_queryset(queryset)
        
        return queryset.select_related('tenant')


class CommentSerializer(CreatedByUserMixin, serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'work_item', 'content', 'created_by', 'created_at', 'updated_at', 'tenant']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant'] 

    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for comment serialization."""
        if queryset is None:
            queryset = Comment.objects.all()
        
        # Use the mixin's optimized queryset
        queryset = super().get_optimized_queryset(queryset)
        
        return queryset.select_related('tenant')
        