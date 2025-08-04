from django.urls import reverse
from rest_framework import status
from relations.tests.client.test_base import FullySetupTest
from relations.tests.factory import (
    create_person, create_organization, create_role
)
from core.models import Role

class TestRoleViews(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.person = create_person(self.tenant)
        self.org = create_organization(self.tenant)
        self.admin_role = create_role(self.tenant, key="admin", label="Admin", is_system=False)
        self.user_role = create_role(self.tenant, key="user", label="User", is_system=False)

    def test_create_role(self):
        self.authenticate_client()
        data = {
            'key': 'test_role',
            'label': 'Test Role',
            'is_system': False,
        }
        url = reverse('core:role-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(role.key, 'test_role')
        self.assertEqual(role.label, 'Test Role')
        self.assertFalse(role.is_system)
        self.assertEqual(role.tenant, self.tenant)

    def test_create_system_role(self):
        self.authenticate_client()
        data = {
            'key': 'tenant_admin',
            'label': 'Tenant Admin',
            'is_system': True,
        }
        url = reverse('core:role-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(role.key, 'tenant_admin')
        self.assertEqual(role.label, 'Tenant Admin')
        self.assertTrue(role.is_system)
        self.assertIsNone(role.tenant)  # System roles have no tenant

    def test_role_unique_constraint(self):
        self.authenticate_client()
        # Create a role with the same key in the same tenant
        create_role(self.tenant, key="duplicate_role", label="Duplicate Role", is_system=False)
        data = {
            'key': 'duplicate_role',
            'label': 'Duplicate Role',
            'is_system': False,
        }
        url = reverse('core:role-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_system_role_unique_constraint(self):
        self.authenticate_client()
        # Create a system role
        create_role(self.tenant, key="tenant_owner", label="Tenant Owner", is_system=True)
        data = {
            'key': 'tenant_owner',
            'label': 'Tenant Owner',
            'is_system': True,
        }
        url = reverse('core:role-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_roles(self):
        self.authenticate_client()
        url = reverse('core:role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see roles for this tenant
        self.assertGreater(len(response.data), 0)

    def test_retrieve_role(self):
        self.authenticate_client()
        url = reverse('core:role-detail', args=[self.admin_role.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], 'Admin') 