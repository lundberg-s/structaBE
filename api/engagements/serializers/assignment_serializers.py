from rest_framework import serializers
from engagements.models import Assignment
from users.serializers.user_serializers import UserWithPersonSerializer

class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['work_item', 'user']

class AssignmentSerializer(serializers.ModelSerializer):
    user = UserWithPersonSerializer(read_only=True)
    assigned_by = UserWithPersonSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'user', 'assigned_by', 'assigned_at'] 