from rest_framework import serializers
from workflow.models import Comment
from user.serializers.user_serializers import UserWithPersonSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserWithPersonSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'work_item', 'content', 'author', 'created_at', 'updated_at', 'tenant']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'tenant'] 