from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status

from users.models import User
from users.permissions import CanManageUsersAndRoles, CanViewContentOnly
from relations.models import Person
from users.serializers.user_serializers import UserSerializer

User = get_user_model()

class UserMeView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        access_token = self.request.COOKIES.get('access_token')
        if not access_token:
            raise AuthenticationFailed('Access token not found in cookies')

        try:
            decoded_token = AccessToken(access_token)
            user_id = decoded_token['user_id']
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

        # Use optimized queryset
        user = UserSerializer.get_optimized_queryset(
            User.objects.filter(id=user_id)
        ).first()
        
        if not user:
            raise AuthenticationFailed('User not found')

        return user

class UserListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        base_queryset = User.objects.filter(tenant=self.request.user.tenant)
        return self.get_serializer_class().get_optimized_queryset(base_queryset)

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
            partner=person
        )
        serializer.instance = user

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class UserDetailView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        base_queryset = User.objects.filter(tenant=self.request.user.tenant)
        return self.get_serializer_class().get_optimized_queryset(base_queryset)
