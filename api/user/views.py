from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed

from user.serializers import UserSerializer


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
    queryset = User.objects.none()
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
