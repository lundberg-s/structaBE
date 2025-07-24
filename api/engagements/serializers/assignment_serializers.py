from rest_framework import serializers
from engagements.models import Assignment
from users.serializers.user_serializers import UserWithPersonSerializer


class AssignmentNameOnlySerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.partner.person.first_name')
    last_name = serializers.CharField(source='user.partner.person.last_name')

    class Meta:
        model = Assignment
        fields = ['id', 'first_name', 'last_name']

class AssignmentSerializer(serializers.ModelSerializer):
    user = UserWithPersonSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'user']


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['work_item', 'user']
        fields = ['id', 'user', 'created_by', 'created_at'] 