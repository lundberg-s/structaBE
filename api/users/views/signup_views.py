from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from users.models import User, Tenant
from core.models import Tenant
from relations.models import Person, Organization, Role, PartnerRoleTypes
from users.serializers.signup_serializers import SignupSerializer

class SignupView(CreateAPIView):
    serializer_class = SignupSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 1. Create Organization (Partner)
        org = Organization.objects.create(
            name=serializer.validated_data['company_name'],
            organization_number=serializer.validated_data.get('organization_number', '')
        )
        # 2. Create Tenant
        tenant = Tenant.objects.create(
            partner=org,
            billing_email=serializer.validated_data['billing_email'],
            billing_address=serializer.validated_data['billing_address'],
        )
        # 3. Create Person (Partner)
        person = Person.objects.create(
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            email=serializer.validated_data['email'],
            phone=serializer.validated_data.get('phone', '')
        )
        # 4. Create User
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            tenant=tenant,
            partner=person,
        )
        # 5. Assign admin role to person
        Role.objects.create(partner=person, role_type=PartnerRoleTypes.TENANT_OWNER)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)