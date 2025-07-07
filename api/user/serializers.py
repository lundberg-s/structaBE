from rest_framework import serializers

from user.models import User, Person, Tenant, Organization, Partner


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id","work_item_type"]


class PartnerSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = ['id', 'role', 'content_type']

    def get_role(self, obj):
        role = obj.roles.first()
        return role.get_role_type_display() if role else None

    def get_content_type(self, obj):
        return obj._meta.model_name

class PersonSerializer(PartnerSerializer):
    class Meta(PartnerSerializer.Meta):
        model = Person
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'role',
            'content_type',
        ]

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


class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    person = PersonSerializer(source='partner.person', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'tenant', 'person']


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    tenant_id = serializers.UUIDField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_tenant_id(self, value):
        if not Tenant.objects.filter(id=value).exists():
            raise serializers.ValidationError("Tenant does not exist.")
        return value


class SignupSerializer(serializers.Serializer):
    # Company fields
    company_name = serializers.CharField()
    organization_number = serializers.CharField(required=False, allow_blank=True)
    billing_email = serializers.EmailField()
    billing_address = serializers.CharField()
    # Rep (user) fields
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_company_name(self, value):
        if Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError("An organization with this name already exists.")
        return value


class FlatOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'organization_number']

class FlatPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']
