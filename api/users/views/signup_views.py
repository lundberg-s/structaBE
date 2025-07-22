from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from users.models import User, Tenant
from core.models import Tenant
from relations.models import Person, Organization, Role
from relations.choices import SystemRole
from relations.tests.factory import create_relation_reference_for_person
from users.serializers.signup_serializers import SignupSerializer
from users.serializers.user_serializers import UserSerializer

class SignupView(CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            return Response(
                {"detail": "Authenticated users cannot sign up again."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 1. Create Tenant
        tenant = Tenant.objects.create(
            billing_email=serializer.validated_data['billing_email'],
            billing_address=serializer.validated_data['billing_address'],
        )
        # 2. Create Organization with tenant
        org = Organization.objects.create(
            name=serializer.validated_data['company_name'],
            organization_number=serializer.validated_data.get('organization_number', ''),
            tenant=tenant
        )
        # 3. Create Person with tenant
        person = Person.objects.create(
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            email=serializer.validated_data['email'],
            phone=serializer.validated_data.get('phone', ''),
            tenant=tenant
        )
        # 4. Create User
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            tenant=tenant,
            partner=person,
        )
        # 5. Create RelationReference for person and assign admin role
        person_ref = create_relation_reference_for_person(person)
        Role.objects.create(
            tenant=tenant,
            target=person_ref,
            system_role=SystemRole.TENANT_OWNER
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)