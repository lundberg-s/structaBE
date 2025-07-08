from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.utilities import (
    set_access_token_cookie,
    set_refresh_token_cookie,
    delete_token_cookies,
)


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Use the built-in serializer directly instead of mutating request.data
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data.get("access")
        refresh_token = serializer.validated_data.get("refresh")

        res = Response(status=status.HTTP_200_OK)
        set_access_token_cookie(res, access_token)
        set_refresh_token_cookie(res, refresh_token)

        return res


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data.get("access")
        res = Response(status=status.HTTP_200_OK)
        set_access_token_cookie(res, access_token)

        return res


class CookieTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenVerifySerializer(data={'token': access_token})
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        res = Response({'message': 'Logged out'})
        delete_token_cookies(res)
        return res
