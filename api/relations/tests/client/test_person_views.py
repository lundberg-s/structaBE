from relations.tests.client.test_base import FullySetupTest
from django.urls import reverse
from partners.models import Person

class TestPersonFlow(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.person_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
        }

    def test_create_person_success(self):
        self.authenticate_client()
        url = reverse('relations:person-list')
        response = self.client.post(url, self.person_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        person = Person.objects.get(id=response.data['id'])
        self.assertEqual(person.first_name, self.person_data['first_name'])
        self.assertEqual(person.tenant, self.tenant)

    def test_list_persons_for_user_tenant_only(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        url = reverse('relations:person-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for person in response.data:
            self.assertEqual(person['tenant'], str(self.tenant.id))

    def test_retrieve_person(self):
        self.authenticate_client()
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        url = reverse('relations:person-detail', args=[person.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(person.id))

    def test_update_person(self):
        self.authenticate_client()
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        url = reverse('relations:person-detail', args=[person.id])
        data = {'first_name': 'Jane'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        person.refresh_from_db()
        self.assertEqual(person.first_name, 'Jane')

    def test_delete_person(self):
        self.authenticate_client()
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        url = reverse('relations:person-detail', args=[person.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Person.objects.filter(id=person.id).exists())

    def test_unauthenticated_user_cannot_create(self):
        url = reverse('relations:person-list')
        response = self.client.post(url, self.person_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_retrieve_person_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        url = reverse('relations:person-detail', args=[person.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_person_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        url = reverse('relations:person-detail', args=[person.id])
        data = {'first_name': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_delete_person_from_other_tenant_fails(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        person = Person.objects.create(tenant=other_tenant, first_name='Jane', last_name='Smith')
        url = reverse('relations:person-detail', args=[person.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Person.objects.filter(id=person.id).exists())

    def test_unauthenticated_user_cannot_get(self):
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        url = reverse('relations:person-detail', args=[person.id])
        self.client.cookies.clear()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_patch(self):
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        url = reverse('relations:person-detail', args=[person.id])
        self.client.cookies.clear()
        response = self.client.patch(url, {'first_name': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_delete(self):
        person = Person.objects.create(tenant=self.tenant, first_name='John', last_name='Doe')
        url = reverse('relations:person-detail', args=[person.id])
        self.client.cookies.clear()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401) 