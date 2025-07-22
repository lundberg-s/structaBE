from relations.tests.client.test_base import FullySetupTest
from relations.models import Partner, Person, Organization, Role
from relations.choices import SystemRole

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
        # Create a RelationReference for the person
        from relations.models import RelationReference
        person_ref = RelationReference.objects.create(
            type='partner',
            partner=person
        )
        role = Role.objects.create(tenant=self.tenant, target=person_ref, system_role=SystemRole.ADMIN)
        self.assertIn('John Doe', str(role))
        self.assertIn('Admin', str(role)) 