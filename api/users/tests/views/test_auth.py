from django.urls import reverse
from django.test import Client
from core.models import Tenant
from users.tests.factory import create_user
from users.tests.client.test_base import FullySetupTest


class TestAuth(FullySetupTest):
    def test_create_user_and_login_view(self):
        self.client.logout()
        user = create_user(
            tenant=self.tenant,
            username='testuser',
            password='testpass',
            email='testuser@example.com'
        )
        
        login_url = reverse('login')
        response = self.client.post(
            login_url,
            {'email': 'testuser@example.com', 'password': 'testpass'},
            format='json'
        )

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    def test_login_with_invalid_credentials(self):
        self.client.logout()
        login_url = reverse('login')
        response = self.client.post(
            login_url,
            {'email': 'testuser@example.com', 'password': 'wrongpass'},
            format='json'
        )

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    def test_login_with_nonexistent_user(self):
        self.client.logout()
        login_url = reverse('login')
        response = self.client.post(
            login_url,
            {'email': 'test@example.com', 'password': 'testpass'},
            format='json'
        )
        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"