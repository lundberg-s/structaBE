from rest_framework import serializers
from engagements.models import Attachment
from users.mixins import CreatedByUserMixin

class AttachmentSerializer(CreatedByUserMixin, serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Attachment
        fields = ['id', 'work_item', 'file', 'filename', 'file_size', 'mime_type', 'created_by', 'tenant']
        read_only_fields = ['id', 'created_by', 'tenant', 'file_size', 'mime_type']
    
    def create(self, validated_data):
        # Calculate file_size from the uploaded file
        if 'file' in validated_data:
            validated_data['file_size'] = validated_data['file'].size
        return super().create(validated_data) 