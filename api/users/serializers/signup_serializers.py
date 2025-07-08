from rest_framework.serializers import Serializer, ValidationError, CharField, EmailField

from users.models import User

from relations.models import Organization

class SignupSerializer(Serializer):
    company_name = CharField()
    organization_number = CharField(required=False, allow_blank=True)
    billing_email = EmailField()
    billing_address = CharField()
    first_name = CharField()
    last_name = CharField()
    email = EmailField()
    password = CharField(write_only=True)
    phone = CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value

    def validate_company_name(self, value):
        if Organization.objects.filter(name=value).exists():
            raise ValidationError("An organization with this name already exists.")
        return value