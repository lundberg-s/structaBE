from relations.tests.client.test_base import FullySetupTest
from relations.models import Partner, Person, Organization
from core.models import Role

class TestModelStrCoverage(FullySetupTest):
    def test_partner_str(self):
        partner = Partner.objects.create(tenant=self.tenant)
        self.assertIsInstance(str(partner), str)

    def test_person_str(self):
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        self.assertEqual(str(person), 'John Doe')

    def test_organization_str(self):
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        self.assertEqual(str(org), 'Test Org')

    def test_role_str(self):
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        role = Role.objects.create(tenant=self.tenant, key="admin", label="Admin", is_system=False)
        self.assertIn('Admin', str(role)) 