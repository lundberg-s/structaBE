from rest_framework import serializers
from engagements.models import Assignment
from users.serializers.user_serializers import UserWithPersonSerializer

class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['work_item', 'user']

class AssignmentSerializer(serializers.ModelSerializer):
    user = UserWithPersonSerializer(read_only=True)
    created_by = UserWithPersonSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'user', 'created_by', 'created_at'] 