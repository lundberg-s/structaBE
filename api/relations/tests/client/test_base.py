from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from users.tests.factory import create_user
from core.models import Tenant

class AuthMixin:
    def authenticate_client(self):
        self.client.cookies['access_token'] = self.token
        # For header-based auth, uncomment:
        # self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'

class FullySetupTest(AuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create()
        cls.password = 'testpass'
        cls.user = create_user(
            tenant=cls.tenant,
            username='testuser',
            password=cls.password,
            email='testuser@example.com'
        )
        cls.client = APIClient()
        login_url = reverse('login')
        login_response = cls.client.post(
            login_url,
            {'email': cls.user.email, 'password': cls.password},
            format='json'
        )
        assert login_response.status_code == 200, "Login failed during setup"
        cls.token = login_response.cookies.get('access_token').value 