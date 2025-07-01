from django.contrib.auth import get_user_model
from diarium.models import Case
from rest_framework.test import APIClient
import uuid

def create_user(username='testuser', email='test@example.com', password='testpass123', **kwargs):
    User = get_user_model()
    return User.objects.create_user(username=username, email=email, password=password, **kwargs)

def create_case(created_by, title='Test Case', status='open', priority='medium', category='General', **kwargs):
    return Case.objects.create(
        title=title,
        description=kwargs.get('description', 'A test case'),
        status=status,
        category=category,
        priority=priority,
        created_by=created_by,
        **kwargs
    )

def authenticate_client(user=None):
    client = APIClient()
    if user is None:
        user = create_user()
    client.force_authenticate(user=user)
    return client, user 