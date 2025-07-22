from django.urls import reverse
from rest_framework import status
from relations.tests.client.test_base import FullySetupTest
from relations.tests.factory import (
    create_person, create_organization, create_relation_reference_for_person, create_relation_reference_for_organization,
    create_custom_role, create_role
)
from relations.models import Role
from relations.choices import SystemRole

class TestRoleViews(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.person = create_person(self.tenant)
        self.org = create_organization(self.tenant)
        self.person_ref = create_relation_reference_for_person(self.person)
        self.org_ref = create_relation_reference_for_organization(self.org)
        self.custom_role = create_custom_role(self.tenant)

    def test_create_role_with_system_role(self):
        self.authenticate_client()
        data = {
            'target': str(self.person_ref.id),
            'system_role': SystemRole.ADMIN,
            'custom_role': None,
        }
        url = reverse('relations:role-list')
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(role.target, self.person_ref)
        self.assertEqual(role.system_role, SystemRole.ADMIN)
        self.assertIsNone(role.custom_role)

    def test_create_role_with_custom_role(self):
        self.authenticate_client()
        data = {
            'target': str(self.org_ref.id),
            'system_role': None,
            'custom_role': self.custom_role.id,
        }
        url = reverse('relations:role-list')
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(role.target, self.org_ref)
        self.assertEqual(role.custom_role, self.custom_role)
        self.assertIsNone(role.system_role)

    def test_role_unique_constraint(self):
        self.authenticate_client()
        create_role(self.tenant, self.person_ref, system_role=SystemRole.ADMIN)
        data = {
            'target': str(self.person_ref.id),
            'system_role': SystemRole.ADMIN,
            'custom_role': None,
        }
        url = reverse('relations:role-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 