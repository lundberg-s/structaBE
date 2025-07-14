from relations.tests.client.test_base import FullySetupTest
from django.urls import reverse
from relations.models import Role, Partner, PartnerRoleTypes
from relations.models import Person, Organization

class TestRoleFlow(FullySetupTest):
    def setUp(self):
        super().setUp()
        # Create a partner (person) for role assignment
        self.person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        self.role_data = {
            'partner': str(self.person.id),
            'role_type': PartnerRoleTypes.ADMIN,
        }

    def test_create_role_success(self):
        self.authenticate_client()
        url = reverse('relations:role-list')
        response = self.client.post(url, self.role_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(str(role.partner.id), self.role_data['partner'])
        self.assertEqual(role.role_type, self.role_data['role_type'])
        self.assertEqual(role.tenant, self.tenant)

    def test_list_roles_for_user_tenant_only(self):
        self.authenticate_client()
        # Create role for another tenant
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        Role.objects.create(tenant=other_tenant, partner=other_person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for role in response.data:
            self.assertEqual(role['tenant'], str(self.tenant.id))

    def test_retrieve_role(self):
        self.authenticate_client()
        role = Role.objects.create(tenant=self.tenant, partner=self.person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(role.id))

    def test_update_role(self):
        self.authenticate_client()
        role = Role.objects.create(tenant=self.tenant, partner=self.person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        data = {'role_type': PartnerRoleTypes.ADMIN}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        role.refresh_from_db()
        self.assertEqual(role.role_type, PartnerRoleTypes.ADMIN)

    def test_delete_role(self):
        self.authenticate_client()
        role = Role.objects.create(tenant=self.tenant, partner=self.person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Role.objects.filter(id=role.id).exists())

    def test_unauthenticated_user_cannot_create(self):
        url = reverse('relations:role-list')
        response = self.client.post(url, self.role_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_retrieve_role_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        role = Role.objects.create(tenant=other_tenant, partner=other_person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_role_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        role = Role.objects.create(tenant=other_tenant, partner=other_person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        data = {'role_type': PartnerRoleTypes.ADMIN}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_delete_role_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        role = Role.objects.create(tenant=other_tenant, partner=other_person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Role.objects.filter(id=role.id).exists())

    def test_unauthenticated_user_cannot_get(self):
        role = Role.objects.create(tenant=self.tenant, partner=self.person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        self.client.cookies.clear()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_patch(self):
        role = Role.objects.create(tenant=self.tenant, partner=self.person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        self.client.cookies.clear()
        response = self.client.patch(url, {'role_type': PartnerRoleTypes.ADMIN}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_delete(self):
        role = Role.objects.create(tenant=self.tenant, partner=self.person, role_type=PartnerRoleTypes.USER)
        url = reverse('relations:role-detail', args=[role.id])
        self.client.cookies.clear()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401) 