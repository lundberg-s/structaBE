from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.contenttypes.models import ContentType

ACCESS_TOKEN_MAX_AGE = 300  # 5 minutes
REFRESH_TOKEN_MAX_AGE = 604800  # 7 days


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            print("No token in cookies.")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            print("Token validation failed:", e)
            return None

        return self.get_user(validated_token), validated_token


def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Strict",
        max_age=ACCESS_TOKEN_MAX_AGE,
    )

def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Strict",
        max_age=REFRESH_TOKEN_MAX_AGE,
    )

def delete_token_cookies(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token") 