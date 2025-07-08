from rest_framework import serializers

from user.models import User, Tenant
from user.serializers.person_serializers import PersonSerializer
from user.serializers.tenant_serializers import TenantSerializer


class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    person = PersonSerializer(source='partner.person', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'tenant', 'person']


class UserWithPersonSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
    
    def _get_partner_person_field(self, obj, field_name):
        if hasattr(obj, 'partner') and obj.partner and hasattr(obj.partner, 'person'):
            return getattr(obj.partner.person, field_name)
        return getattr(obj, field_name) or ''
    
    def get_first_name(self, obj):
        return self._get_partner_person_field(obj, 'first_name')
    
    def get_last_name(self, obj):
        return self._get_partner_person_field(obj, 'last_name')