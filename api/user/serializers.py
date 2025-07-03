from rest_framework import serializers

from user.models import User, Person, Tenant, Organization, Party


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["workitem_type"]


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "organization_number"]


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']


class PartySerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    person = PersonSerializer(read_only=True)
    class Meta:
        model = Party
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    person = PersonSerializer(source='party.person', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'footer_text', 'external_id', 'tenant', 'person']


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
