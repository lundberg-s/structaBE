from rest_framework import serializers
from workflow.models import Attachment
from user.serializers.user_serializers import UserWithPersonSerializer

class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserWithPersonSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Attachment
        fields = ['id', 'work_item', 'file', 'filename', 'file_size', 'mime_type', 'uploaded_by', 'uploaded_at', 'tenant']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'tenant'] 