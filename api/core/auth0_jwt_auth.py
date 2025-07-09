# import json
# import requests
# from jose import jwt
# from django.conf import settings
# from rest_framework import authentication, exceptions
# from urllib.parse import urljoin

# AUTH0_DOMAIN = getattr(settings, 'AUTH0_DOMAIN', None)
# API_IDENTIFIER = getattr(settings, 'AUTH0_API_IDENTIFIER', None)
# ALGORITHMS = getattr(settings, 'AUTH0_ALGORITHMS', ['RS256'])

# class Auth0JSONWebTokenAuthentication(authentication.BaseAuthentication):
#     """
#     DRF authentication class for Auth0 JWTs via Authorization: Bearer <token>.
#     Validates signature, issuer, audience, and expiration.
#     """
#     def authenticate(self, request):
#         auth = request.headers.get('Authorization', None)
#         if not auth:
#             return None
#         parts = auth.split()
#         if parts[0].lower() != 'bearer':
#             raise exceptions.AuthenticationFailed('Authorization header must start with Bearer')
#         if len(parts) == 1:
#             raise exceptions.AuthenticationFailed('Token not found')
#         if len(parts) > 2:
#             raise exceptions.AuthenticationFailed('Authorization header must be Bearer token')
#         token = parts[1]
#         try:
#             payload = self.decode_jwt(token)
#         except Exception as e:
#             raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
#         user = self.get_or_create_user(payload)
#         return (user, payload)

#     def decode_jwt(self, token):
#         jwks_url = urljoin(f'https://{AUTH0_DOMAIN}/', '.well-known/jwks.json')
#         jwks = requests.get(jwks_url).json()
#         unverified_header = jwt.get_unverified_header(token)
#         rsa_key = {}
#         for key in jwks['keys']:
#             if key['kid'] == unverified_header['kid']:
#                 rsa_key = {
#                     'kty': key['kty'],
#                     'kid': key['kid'],
#                     'use': key['use'],
#                     'n': key['n'],
#                     'e': key['e']
#                 }
#         if not rsa_key:
#             raise exceptions.AuthenticationFailed('Unable to find appropriate key')
#         payload = jwt.decode(
#             token,
#             rsa_key,
#             algorithms=ALGORITHMS,
#             audience=API_IDENTIFIER,
#             issuer=f'https://{AUTH0_DOMAIN}/'
#         )
#         return payload

#     def get_or_create_user(self, payload):
#         # Optionally, create or fetch a Django user based on Auth0 sub/email
#         from django.contrib.auth import get_user_model
#         User = get_user_model()
#         sub = payload.get('sub')
#         email = payload.get('email')
#         user, _ = User.objects.get_or_create(username=sub, defaults={'email': email or ''})
#         return user 