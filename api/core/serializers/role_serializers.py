from rest_framework import serializers
from django.core.exceptions import ValidationError
from core.models import Role
from relations.models import Partner

class RoleSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'key', 'label', 'is_system', 'tenant', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate Role data:
        1. System roles must have valid system role keys
        2. Tenant roles can have any key (uniqueness handled by model constraints)
        """
        key = data.get('key')
        is_system = data.get('is_system', False)

        if is_system:
            # System roles must have valid keys
            from core.enums.system_role_enums import SystemRole
            if key not in [role.value for role in SystemRole]:
                raise serializers.ValidationError(
                    f"{key} is not a valid system role key"
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        is_system = validated_data.get('is_system', False)
        
        if is_system:
            # System roles have no tenant
            validated_data['tenant'] = None
        elif request and hasattr(request, 'user'):
            # Custom roles get tenant from request user
            validated_data['tenant'] = request.user.tenant
        
        try:
            return super().create(validated_data)
        except ValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise serializers.ValidationError(e.message_dict) 