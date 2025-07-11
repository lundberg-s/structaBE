import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(tenant, username='testuser', password='testpass', email=None):
    if email is None:
        email = f"{username}@example.com"
    user = User.objects.create_user(username=username, email=email, password=password, tenant=tenant)
    return user
