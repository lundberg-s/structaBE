from rest_framework.serializers import ModelSerializer

from user.serializers.partner_serializers import PartnerSerializer

from user.models import Organization

class OrganizationSerializer(PartnerSerializer):
    class Meta(PartnerSerializer.Meta):
        model = Organization
        fields = [
            'id',
            'name',
            'organization_number',
            'role',
            'content_type',
        ]

class FlatOrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'organization_number']

class FlatPersonSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']