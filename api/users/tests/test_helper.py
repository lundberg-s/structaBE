from core.enums import SystemRole
from core.tests import CoreTestHelper
from users.tests.factory import UserFactory
from users.tests.test_constants import UserTestData
from django.urls import reverse


class UserTestHelper(CoreTestHelper):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.token = self.authenticate_user()

    def create_user(self, email=None, password=None, tenant=None):
        email = email or UserTestData.DEFAULT_USER_EMAIL
        password = password or UserTestData.DEFAULT_USER_PASSWORD
        tenant = tenant or self.tenant

        user = UserFactory.create(
            tenant=tenant,
            username=email.split("@")[0],
            password=password,
            email=email,
        )
        
        return user

    def authenticate_user(self, email=None, password=None):
        email = email or UserTestData.DEFAULT_USER_EMAIL
        password = password or UserTestData.DEFAULT_USER_PASSWORD
        
        response = self.client.post(
            reverse("login"),
            {"email": email, "password": password},
            format="json",
        )
        assert response.status_code == 200, "Login failed during setup"
        return response.cookies.get("access_token").value
