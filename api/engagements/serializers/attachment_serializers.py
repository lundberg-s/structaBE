from rest_framework import serializers
from engagements.models import Attachment
from users.serializers.user_serializers import UserWithPersonSerializer

class AttachmentSerializer(serializers.ModelSerializer):
    created_by = UserWithPersonSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Attachment
        fields = ['id', 'work_item', 'file', 'filename', 'file_size', 'mime_type', 'created_by', 'tenant']
        read_only_fields = ['id', 'created_by', 'tenant'] 