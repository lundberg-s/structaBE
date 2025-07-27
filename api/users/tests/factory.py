import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(tenant, username='testuser', password='testpass', email=None):
    if email is None:
        # Generate unique email using tenant ID and username
        email = f"{username}_{tenant.id}@example.com"
    user = User.objects.create_user(email=email, password=password, tenant=tenant, username=username)
    return user
