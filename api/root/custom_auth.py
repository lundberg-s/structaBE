from rest_framework_simplejwt.authentication import JWTAuthentication

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
