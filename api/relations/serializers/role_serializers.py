from rest_framework import serializers
from relations.models import Role, Partner, PartnerRoleTypes

class RoleSerializer(serializers.ModelSerializer):
    partner = serializers.PrimaryKeyRelatedField(queryset=Partner.objects.all())
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)
    role_type = serializers.ChoiceField(choices=PartnerRoleTypes.choices)

    class Meta:
        model = Role
        fields = ['id', 'partner', 'role_type', 'tenant', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['tenant'] = request.user.tenant
        return super().create(validated_data) 