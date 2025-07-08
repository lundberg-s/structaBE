from rest_framework import serializers
from engagements.models import ActivityLog
from users.serializers.user_serializers import UserWithPersonSerializer

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserWithPersonSerializer(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ActivityLog
        fields = ['id', 'work_item', 'activity_type', 'description', 'user', 'created_at', 'tenant']
        read_only_fields = ['id', 'user', 'created_at', 'tenant'] 