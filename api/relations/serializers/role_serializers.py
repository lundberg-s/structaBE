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

    def validate(self, data):
        """
        Validate Role data:
        1. Either system_role OR custom_role must be set
        2. Cannot have both system_role AND custom_role
        """
        system_role = data.get('system_role')
        custom_role = data.get('custom_role')

        # 1. Validate exactly one role type is set
        if not system_role and not custom_role:
            raise serializers.ValidationError(
                "Either system_role or custom_role must be set"
            )

        # 2. Validate not both role types are set
        if system_role and custom_role:
            raise serializers.ValidationError(
                "Only one of system_role or custom_role can be set"
            )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['tenant'] = request.user.tenant
        return super().create(validated_data) 