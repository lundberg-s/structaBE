from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_ticket
from engagements.models import WorkItemPartnerRole, Ticket
from relations.models import Organization, Person
from django.contrib.contenttypes.models import ContentType
from engagements.tests.client.test_base import FullySetupTest

class TestWorkItemPartnerRoleFlow(FullySetupTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.work_item = self.ticket
        self.organization = Organization.objects.create(tenant=self.tenant, name='Test Org')
        self.person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        self.org_content_type = ContentType.objects.get_for_model(Organization)
        self.person_content_type = ContentType.objects.get_for_model(Person)
        self.role_data = {
            'work_item': str(self.work_item.id),
            'content_type': 'organization',  # <-- as a string
            'object_id': str(self.organization.id),  # <-- as a string
            'role': 'customer',
        }

    def authenticate(self):
        self.authenticate_client()

    def test_create_partner_role_success(self):
        self.authenticate()
        url = reverse('engagements:work_item-partner-role-list')
        response = self.client.post(url, self.role_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        role = WorkItemPartnerRole.objects.get(id=response.data['id'])
        self.assertEqual(str(role.work_item.id), str(self.work_item.id))
        self.assertEqual(role.partner, self.organization)
        self.assertEqual(role.role, 'customer')

    def test_create_partner_role_with_person(self):
        self.authenticate()
        url = reverse('engagements:work_item-partner-role-list')
        data = self.role_data.copy()
        data['content_type'] = 'person'
        data['object_id'] = str(self.person.id)
        data['role'] = 'vendor'
        response = self.client.post(url, data)
        self.assertIn(response.status_code, (200, 201))
        role = WorkItemPartnerRole.objects.get(id=response.data['id'])
        self.assertEqual(role.partner, self.person)
        self.assertEqual(role.role, 'vendor')

    def test_list_partner_roles(self):
        self.authenticate()
        WorkItemPartnerRole.objects.create(
            tenant=self.tenant,
            work_item=self.work_item,  # Pass instance, not UUID
            content_type=self.org_content_type,  # Pass ContentType instance
            object_id=self.organization.id,
            role='customer',
        )
        url = reverse('engagements:work_item-partner-role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(r['role'] == 'customer' for r in response.data))

    def test_retrieve_partner_role(self):
        self.authenticate()
        role = WorkItemPartnerRole.objects.create(
            tenant=self.tenant,
            work_item=self.work_item,  # Pass instance
            content_type=self.org_content_type,  # Pass ContentType instance
            object_id=self.organization.id,
            role='customer',
        )
        url = reverse('engagements:work_item-partner-role-detail', args=[role.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['role'], 'customer')

    def test_update_partner_role(self):
        self.authenticate()
        role = WorkItemPartnerRole.objects.create(
            tenant=self.tenant,
            work_item=self.work_item,  # Pass instance
            content_type=self.org_content_type,  # Pass ContentType instance
            object_id=self.organization.id,
            role='customer',
        )
        url = reverse('engagements:work_item-partner-role-detail', args=[role.id])
        data = {
            'work_item': str(self.work_item.id),  # For PATCH, pass UUID as string
            'content_type': 'organization',  # For PATCH, pass as string
            'object_id': str(self.organization.id),
            'role': 'vendor',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        role.refresh_from_db()
        self.assertEqual(role.role, 'vendor')

    def test_delete_partner_role(self):
        self.authenticate()
        role = WorkItemPartnerRole.objects.create(
            tenant=self.tenant,
            work_item=self.work_item,  # Pass instance
            content_type=self.org_content_type,  # Pass ContentType instance
            object_id=self.organization.id,
            role='customer',
        )
        url = reverse('engagements:work_item-partner-role-detail', args=[role.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(WorkItemPartnerRole.objects.filter(id=role.id).exists())

    def test_cannot_create_duplicate_role(self):
        self.authenticate()
        WorkItemPartnerRole.objects.create(
            tenant=self.tenant,
            work_item=self.work_item,  # Pass instance
            content_type=self.org_content_type,  # Pass ContentType instance
            object_id=self.organization.id,
            role='customer',
        )
        url = reverse('engagements:work_item-partner-role-list')
        response = self.client.post(url, self.role_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_partner_role_scoped_to_tenant(self):
        self.authenticate()
        other_tenant = create_tenant()
        other_org = Organization.objects.create(tenant=other_tenant, name='Other Org')
        WorkItemPartnerRole.objects.create(
            tenant=other_tenant,
            work_item=self.work_item,  # Pass instance
            content_type=ContentType.objects.get_for_model(Organization),
            object_id=other_org.id,
            role='customer',
        )
        url = reverse('engagements:work_item-partner-role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for r in response.data:
            self.assertEqual(str(r['tenant']), str(self.tenant.id))
