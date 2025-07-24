from rest_framework import serializers
from engagements.models import Comment
from users.serializers.user_serializers import UserWithPersonSerializer

class CommentListSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = UserWithPersonSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'work_item', 'content', 'created_by', 'created_at', 'updated_at', 'tenant']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tenant'] 

    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for comment serialization."""
        if queryset is None:
            queryset = Comment.objects.all()
        
        return queryset.select_related('created_by__partner__person', 'tenant')

class CommentSerializer(serializers.ModelSerializer):
    created_by = UserWithPersonSerializer(read_only=True)
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
        
        return queryset.select_related('created_by__partner__person', 'tenant')
        