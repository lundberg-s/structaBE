from rest_framework import serializers

from users.models import User
from relations.serializers.person_serializers import PersonSerializer
from core.serializers.tenant_serializers import TenantSerializer


class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    person = PersonSerializer(source='partner.person', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'tenant', 'person']

    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for user serialization."""
        if queryset is None:
            queryset = User.objects.all()
        
        return queryset.select_related(
            'tenant',
            'partner__person'
        )


class UserWithPersonSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='partner.person.first_name', default='')
    last_name = serializers.CharField(source='partner.person.last_name', default='')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
    
    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized for user with person serialization."""
        if queryset is None:
            queryset = User.objects.all()
        
        return queryset.select_related(
            'partner__person'
        )