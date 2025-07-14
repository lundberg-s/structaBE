import pytest
from django.urls import reverse
from django.test import Client
from core.models import Tenant
from users.tests.factory import create_user

@pytest.mark.django_db
def test_create_user_and_login_view():
    tenant = Tenant.objects.create()
    user = create_user(
        tenant=tenant,
        username='testuser',
        password='testpass',
        email='testuser@example.com'
    )
    client = Client()

    login_url = reverse('login')
    response = client.post(
        login_url,
        {'email': 'testuser@example.com', 'password': 'testpass'},
        content_type='application/json'
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

@pytest.mark.django_db
def test_login_with_invalid_credentials():
    client = Client()
    login_url = reverse('login')
    response = client.post(
        login_url,
        {'email': 'testuser@example.com', 'password': 'wrongpass'},
        content_type='application/json'
    )

    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"


@pytest.mark.django_db
def test_login_with_nonexistent_user():
    client = Client()
    login_url = reverse('login')
    response = client.post(
        login_url,
        {'email': 'test@example.com', 'password': 'testpass'},
        content_type='application/json'
    )
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"