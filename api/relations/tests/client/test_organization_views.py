from rest_framework.test import APITestCase, APIClient
from relations.tests.client.test_base import FullySetupTest
from django.urls import reverse
from relations.models import Organization

class TestOrganizationFlow(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.org_data = {
            'name': 'Test Org',
            'organization_number': 'ORG-001',
        }

    def test_create_organization_success(self):
        self.authenticate_client()
        url = reverse('relations:organization-list')
        response = self.client.post(url, self.org_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        org = Organization.objects.get(id=response.data['id'])
        self.assertEqual(org.name, self.org_data['name'])
        self.assertEqual(org.tenant, self.tenant)

    def test_list_organizations_for_user_tenant_only(self):
        self.authenticate_client()
        # Create org for another tenant
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        Organization.objects.create(tenant=other_tenant, name='Other Org')
        url = reverse('relations:organization-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for org in response.data:
            self.assertEqual(org['tenant'], str(self.tenant.id))

    def test_retrieve_organization(self):
        self.authenticate_client()
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        url = reverse('relations:organization-detail', args=[org.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(org.id))

    def test_update_organization(self):
        self.authenticate_client()
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        url = reverse('relations:organization-detail', args=[org.id])
        data = {'name': 'Updated Org'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        org.refresh_from_db()
        self.assertEqual(org.name, 'Updated Org')

    def test_delete_organization(self):
        self.authenticate_client()
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        url = reverse('relations:organization-detail', args=[org.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Organization.objects.filter(id=org.id).exists())

    def test_unauthenticated_user_cannot_create(self):
        url = reverse('relations:organization-list')
        response = self.client.post(url, self.org_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_retrieve_organization_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        org = Organization.objects.create(tenant=other_tenant, name='Other Org')
        url = reverse('relations:organization-detail', args=[org.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_organization_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        org = Organization.objects.create(tenant=other_tenant, name='Other Org')
        url = reverse('relations:organization-detail', args=[org.id])
        data = {'name': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_delete_organization_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        org = Organization.objects.create(tenant=other_tenant, name='Other Org')
        url = reverse('relations:organization-detail', args=[org.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Organization.objects.filter(id=org.id).exists())

    def test_unauthenticated_user_cannot_get(self):
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        url = reverse('relations:organization-detail', args=[org.id])
        self.client.cookies.clear()  # Remove auth
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_patch(self):
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        url = reverse('relations:organization-detail', args=[org.id])
        self.client.cookies.clear()
        response = self.client.patch(url, {'name': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_delete(self):
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        url = reverse('relations:organization-detail', args=[org.id])
        self.client.cookies.clear()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401) 