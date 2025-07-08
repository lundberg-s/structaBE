from rest_framework import serializers
from engagements.models import WorkItemPartnerRole
from relations.models import Organization, Person
from relations.serializers.person_serializers import PersonSerializer, FlatPersonSerializer
from relations.serializers.organization_serializers import OrganizationSerializer, FlatOrganizationSerializer
from relations.serializers.partner_serializers import PartnerSerializer

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

class WorkItemPartnerRoleNestedSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)
    class Meta:
        model = WorkItemPartnerRole
        fields = ['id', 'partner']

class FlatPartnerWithRoleSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        partner = obj.partner
        if partner is None:
            return None
        if isinstance(partner, Organization):
            data = dict(FlatOrganizationSerializer(partner).data)
            data['role'] = obj.role
            data['content_type'] = obj.content_type.model
            return {
                'organization': data
            }
        elif isinstance(partner, Person):
            data = dict(FlatPersonSerializer(partner).data)
            data['role'] = obj.role
            data['content_type'] = obj.content_type.model
            return {
                'person': data
            }
        else:
            data = {}
            data['role'] = obj.role
            data['content_type'] = obj.content_type.model if obj.content_type else None
            return {
                'unknown': data
            }

class WorkItemPartnerRoleCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.filter(model__in=['person', 'organization']),
        slug_field='model'
    )
    object_id = serializers.UUIDField()

    class Meta:
        model = WorkItemPartnerRole
        fields = ['work_item', 'content_type', 'object_id', 'role']

    def validate(self, attrs):
        content_type = attrs.get('content_type')
        object_id = attrs.get('object_id')
        model_class = content_type.model_class()
        if not model_class.objects.filter(id=object_id).exists():
            raise ValidationError({'object_id': 'No matching object found for this content type.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('partner_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('partner_id', None)
        return super().update(instance, validated_data)

class WorkItemPartnerRoleGetSerializer(serializers.ModelSerializer):
    partner = serializers.SerializerMethodField()

    class Meta:
        model = WorkItemPartnerRole
        fields = ['id', 'partner', 'role', 'tenant']

    def get_partner(self, obj):
        partner = obj.partner
        if isinstance(partner, Organization):
            return OrganizationSerializer(partner).data
        elif isinstance(partner, Person):
            return PersonSerializer(partner).data
        return None 