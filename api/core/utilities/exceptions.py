# from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If the exception is an IntegrityError, return a 400 response
    if isinstance(exc, IntegrityError):
        return Response(
            {'error': 'A record with this data already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return response 