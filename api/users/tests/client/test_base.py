from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from core.models import Tenant
from users.models import User
from users.tests.factory import create_user

class FullySetupTest(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create()  # type: ignore[attr-defined]
        self.user = create_user(
            tenant=self.tenant,
            username='mainuser',
            password='mainpass',
            email='mainuser@example.com'
        )
        self.client = APIClient()
        self.login_user(self.user)

    def login_user(self, user=None, password='mainpass'):
        if user is None:
            user = self.user
        login_url = reverse('login')
        response = self.client.post(
            login_url,
            {'email': user.email, 'password': password},
            format='json'
        )
        # DRF APIClient returns a Response with status_code and content attributes
        assert getattr(response, 'status_code', None) == 200, f"Login failed: {getattr(response, 'content', '')}" 