from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from user.models import User, Person, Tenant, Organization, Party
from user.serializers import (
    UserSerializer, PersonSerializer, SignupSerializer, OrganizationSerializer
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

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


class UserListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        # Create a Person instance
        person = Person.objects.create(
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            email=serializer.validated_data.get('email', ''),
            phone=serializer.validated_data.get('phone', ''),
            tenant=self.request.user.tenant
        )
        # Create a User instance and associate with the Person
        user = User.objects.create_user(
            email=person.email,
            password=serializer.validated_data.get('password', ''),
            tenant=self.request.user.tenant,
            party=person
        )
        serializer.instance = user

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class UserDetailView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)
