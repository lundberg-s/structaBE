from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from user.models import User, Person, Tenant, Organization
from user.serializers import (
    UserSerializer, PersonSerializer, UserRegistrationSerializer, CompanyUserRegistrationSerializer
)


User = get_user_model()

class UserMeView(RetrieveAPIView):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    def get_object(self):
        access_token = self.request.COOKIES.get('access_token')
        if not access_token:
            raise AuthenticationFailed('Access token not found in cookies')

        try:
            decoded_token = AccessToken(access_token)
            user_id = decoded_token['user_id']
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

        user = User.objects.filter(id=user_id).first()
        if not user:
            raise AuthenticationFailed('User not found')

        return user


class UserListView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(party__tenant=self.request.user.party.tenant)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Create Person (Party)
        person = Person.objects.create(
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            email=serializer.validated_data['email'],
            phone=serializer.validated_data.get('phone', '')
        )
        # Get Tenant
        tenant = Tenant.objects.get(id=serializer.validated_data['tenant_id'])
        # Create User
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            tenant=tenant,
            party=person,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class PersonDetailView(generics.RetrieveAPIView):
    serializer_class = PersonSerializer

    def get_queryset(self):
        return Person.objects.filter(tenant=self.request.user.party.tenant)

class PersonListView(generics.ListAPIView):
    serializer_class = PersonSerializer

    def get_queryset(self):
        return Person.objects.filter(tenant=self.request.user.party.tenant)

class CompanyUserRegistrationView(generics.CreateAPIView):
    serializer_class = CompanyUserRegistrationSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 1. Create Organization (Party)
        org = Organization.objects.create(
            name=serializer.validated_data['company_name'],
            organization_number=serializer.validated_data.get('organization_number', '')
        )
        # 2. Create Tenant
        tenant = Tenant.objects.create(
            party=org,
            billing_email=serializer.validated_data['billing_email'],
            billing_address=serializer.validated_data['billing_address'],
        )
        # 3. Create Person (Party)
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
            party=person,
        )
        # 5. Assign admin role to person
        from user.models import Role
        Role.objects.create(party=person, role_type='tenant')
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
