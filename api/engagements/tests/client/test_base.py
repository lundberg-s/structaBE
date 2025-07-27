from django.test import TestCase, Client
from django.urls import reverse
from users.tests.factory import create_user
from engagements.tests.factory import create_ticket
from relations.tests.factory import create_person, create_role
from relations.choices import SystemRole
from core.models import Tenant

class AuthMixin:
    def authenticate_client(self):
        """Set up authentication for the test client."""
        # For cookie-based auth
        self.client.cookies['access_token'] = self.token

        # For header-based auth (uncomment if you switch to header auth)
        # self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'

class FullySetupTest(AuthMixin, TestCase):
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

        # Create a person for the user and assign tenant_employee role
        person = create_person(tenant=cls.tenant, first_name='Test', last_name='User')
        role = create_role(tenant=cls.tenant, key=SystemRole.TENANT_EMPLOYEE.value, label=SystemRole.TENANT_EMPLOYEE.label, is_system=True)
        person.role = role
        person.save()
        cls.user.partner = person
        cls.user.save()

        cls.client = Client()
        login_url = reverse('login')
        login_response = cls.client.post(
            login_url,
            {'email': cls.user.email, 'password': cls.password},
            content_type='application/json'
        )
        assert login_response.status_code == 200, "Login failed during setup"

        cls.token = login_response.cookies.get('access_token').value 

        cls.ticket = create_ticket(tenant=cls.tenant, created_by=cls.user)


class TicketTenancySetup(AuthMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(work_item_type='ticket')
        cls.password = 'testpass'

        cls.user = create_user(
            tenant=cls.tenant,
            username='testuser',
            password=cls.password,
            email='testuser@example.com'
        )

        # Create a person for the user and assign tenant_employee role
        person = create_person(tenant=cls.tenant, first_name='Test', last_name='User')
        role = create_role(tenant=cls.tenant, key=SystemRole.TENANT_EMPLOYEE.value, label=SystemRole.TENANT_EMPLOYEE.label, is_system=True)
        person.role = role
        person.save()
        cls.user.partner = person
        cls.user.save()

        cls.client = Client()
        login_url = reverse('login')
        login_response = cls.client.post(
            login_url,
            {'email': cls.user.email, 'password': cls.password},
            content_type='application/json'
        )
        assert login_response.status_code == 200, "Login failed during setup"

        cls.token = login_response.cookies.get('access_token').value 

        cls.ticket = create_ticket(tenant=cls.tenant, created_by=cls.user)



class JobTenancySetup(AuthMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(work_item_type='job')
        cls.password = 'testpass'

        cls.user = create_user(
            tenant=cls.tenant,
            username='testuser',
            password=cls.password,
            email='testuser@example.com'
        )

        # Create a person for the user and assign tenant_employee role
        person = create_person(tenant=cls.tenant, first_name='Test', last_name='User')
        role = create_role(tenant=cls.tenant, key=SystemRole.TENANT_EMPLOYEE.value, label=SystemRole.TENANT_EMPLOYEE.label, is_system=True)
        person.role = role
        person.save()
        cls.user.partner = person
        cls.user.save()

        cls.client = Client()
        login_url = reverse('login')
        login_response = cls.client.post(
            login_url,
            {'email': cls.user.email, 'password': cls.password},
            content_type='application/json'
        )
        assert login_response.status_code == 200, "Login failed during setup"

        cls.token = login_response.cookies.get('access_token').value 

        cls.ticket = create_ticket(tenant=cls.tenant, created_by=cls.user)


class CaseTenancySetup(AuthMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(work_item_type='case')
        cls.password = 'testpass'

        cls.user = create_user(
            tenant=cls.tenant,
            username='testuser',
            password=cls.password,
            email='testuser@example.com'
        )

        # Create a person for the user and assign tenant_employee role
        person = create_person(tenant=cls.tenant, first_name='Test', last_name='User')
        role = create_role(tenant=cls.tenant, key=SystemRole.TENANT_EMPLOYEE.value, label=SystemRole.TENANT_EMPLOYEE.label, is_system=True)
        person.role = role
        person.save()
        cls.user.partner = person
        cls.user.save()

        cls.client = Client()
        login_url = reverse('login')
        login_response = cls.client.post(
            login_url,
            {'email': cls.user.email, 'password': cls.password},
            content_type='application/json'
        )
        assert login_response.status_code == 200, "Login failed during setup"

        cls.token = login_response.cookies.get('access_token').value 

        cls.ticket = create_ticket(tenant=cls.tenant, created_by=cls.user)
