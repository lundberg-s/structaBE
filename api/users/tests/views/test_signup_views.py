from django.urls import reverse
from users.models import User
from users.tests.client.test_base import FullySetupTest

class TestSignupViews(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.signup_url = reverse('users:sign-up')
        self.valid_data = {
            'company_name': 'TestOrg',
            'organization_number': '12345',
            'billing_email': 'billing@example.com',
            'billing_address': '123 Main St',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'password': 'testpass',
            'phone': '555-1234',
        }

    def test_signup_happy_path(self):
        self.client.logout()  # Signup should be unauthenticated
        response = self.client.post(self.signup_url, self.valid_data, format='json')
        assert getattr(response, 'status_code', None) == 201
        assert User.objects.filter(email='alice@example.com').exists()

    def test_signup_duplicate_email(self):
        self.client.logout()
        User.objects.create_user(email='alice@example.com', password='testpass', tenant=self.tenant)
        response = self.client.post(self.signup_url, self.valid_data, format='json')
        assert getattr(response, 'status_code', None) == 400
        assert 'email' in str(getattr(response, 'data', {}))

    def test_signup_duplicate_org(self):
        self.client.logout()
        # First signup
        self.client.post(self.signup_url, self.valid_data, format='json')
        # Second signup with same org name
        data2 = self.valid_data.copy()
        data2['email'] = 'bob@example.com'
        response = self.client.post(self.signup_url, data2, format='json')
        assert getattr(response, 'status_code', None) == 400
        assert 'company_name' in str(getattr(response, 'data', {}))

    def test_signup_invalid_data(self):
        self.client.logout()
        data = self.valid_data.copy()
        data['email'] = 'not-an-email'
        response = self.client.post(self.signup_url, data, format='json')
        assert getattr(response, 'status_code', None) == 400
        assert 'email' in str(getattr(response, 'data', {}))

    def test_signup_authenticated_forbidden(self):
        # Authenticated users should not be able to sign up again
        response = self.client.post(self.signup_url, self.valid_data, format='json')
        assert getattr(response, 'status_code', None) in (403, 400) 