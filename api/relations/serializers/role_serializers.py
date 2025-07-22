from rest_framework import serializers
from relations.models import Role, RelationReference, CustomRole
from relations.choices import SystemRole

class RoleSerializer(serializers.ModelSerializer):
    target = serializers.PrimaryKeyRelatedField(queryset=RelationReference.objects.all())
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    system_role = serializers.ChoiceField(choices=SystemRole.choices, required=False, allow_null=True)
    custom_role = serializers.PrimaryKeyRelatedField(queryset=CustomRole.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Role
        fields = ['id', 'target', 'system_role', 'custom_role', 'tenant', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['tenant'] = request.user.tenant
        return super().create(validated_data) 