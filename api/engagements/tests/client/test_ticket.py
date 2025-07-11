from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_ticket
from engagements.tests.client.test_base import TicketTenancySetup
from engagements.models import Ticket
from datetime import timedelta
from django.utils import timezone

class TestTicketFlow(TicketTenancySetup, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.ticket_data = {
            'title': 'Test Ticket',
            'description': 'A test ticket',
            'status': 'open',
            'category': 'ticket',
            'priority': 'medium',
            'deadline': (timezone.now() + timedelta(days=7)).isoformat(),
            'ticket_number': 'T-001',
            'reported_by': 'Reporter',
            'urgency': 'medium',
        }

    def test_create_ticket_success(self):
        self.authenticate_client()
        url = reverse('engagements:ticket-list')
        response = self.client.post(url, self.ticket_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        ticket = Ticket.objects.get(id=response.data['id'])
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_create_ticket_auto_sets_user_and_tenant(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        other_tenant = create_tenant()
        url = reverse('engagements:ticket-list')
        data = self.ticket_data.copy()
        data['created_by'] = other_user.id
        data['tenant'] = other_tenant.id
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        ticket = Ticket.objects.get(id=response.data['id'])
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_create_ticket_invalid_foreign_key(self):
        self.authenticate_client()
        url = reverse('engagements:ticket-list')
        # Invalid category
        data = self.ticket_data.copy()
        data['category'] = 'invalid'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid status
        data = self.ticket_data.copy()
        data['status'] = 'invalid'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_ticket(self):
        url = reverse('engagements:ticket-list')
        response = self.client.post(url, self.ticket_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_list_tickets_for_user_tenant_only(self):
        self.authenticate_client()
        # Create ticket for another tenant
        other_tenant = create_tenant()
        create_ticket(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for ticket in response.data:
            self.assertEqual(ticket['tenant'], self.tenant.id)

    def test_retrieve_ticket_from_same_tenant(self):
        self.authenticate_client()
        ticket = create_ticket(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['id']), str(ticket.id))

    def test_retrieve_ticket_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_ticket_success(self):
        self.authenticate_client()
        ticket = create_ticket(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.title, 'Updated Title')

    def test_update_ticket_from_other_user_fails(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        ticket = create_ticket(tenant=self.tenant, created_by=other_user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_update_ticket_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_cannot_spoof_protected_fields_on_update(self):
        self.authenticate_client()
        ticket = create_ticket(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        data = {'created_by': create_user(tenant=self.tenant, username='spoof', password='pass').id, 'tenant': create_tenant().id}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_delete_own_ticket_success(self):
        self.authenticate_client()
        ticket = create_ticket(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())

    def test_delete_ticket_from_other_user_fails(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        ticket = create_ticket(tenant=self.tenant, created_by=other_user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ticket.objects.filter(id=ticket.id).exists())

    def test_delete_ticket_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Ticket.objects.filter(id=ticket.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        ticket = create_ticket(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:ticket-detail', args=[ticket.id])
        data = {'created_at': '2000-01-01T00:00:00Z'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertNotEqual(str(ticket.created_at), '2000-01-01T00:00:00Z')

    def test_cannot_spoof_protected_fields_on_create(self):
        self.authenticate_client()
        url = reverse('engagements:ticket-list')
        data = self.ticket_data.copy()
        data['created_by'] = create_user(tenant=self.tenant, username='spoof', password='pass').id
        data['tenant'] = create_tenant().id
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        ticket = Ticket.objects.get(id=response.data['id'])
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_http_status_codes_are_correct(self):
        self.authenticate_client()
        url = reverse('engagements:ticket-list')
        # Valid create
        response = self.client.post(url, self.ticket_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        # Invalid create
        data = self.ticket_data.copy()
        data['category'] = 'invalid'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Unauthenticated
        self.client.logout()
        response = self.client.post(url, self.ticket_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_denied(self):
        url = reverse('engagements:ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_tickets_by_status_and_priority(self):
        self.authenticate_client()
        t1 = create_ticket(tenant=self.tenant, created_by=self.user)
        t1.status = 'open'
        t1.priority = 'high'
        t1.save()
        t2 = create_ticket(tenant=self.tenant, created_by=self.user)
        t2.status = 'closed'
        t2.priority = 'low'
        t2.save()
        url = reverse('engagements:ticket-list') + '?status=open&priority=high'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for ticket in response.data:
            self.assertEqual(ticket['status'], 'open')
            self.assertEqual(ticket['priority'], 'high')

    def test_search_tickets_by_title_or_description(self):
        self.authenticate_client()
        t = create_ticket(tenant=self.tenant, created_by=self.user)
        t.title = 'UniqueTitle'
        t.description = 'SpecialDesc'
        t.save()
        url = reverse('engagements:ticket-list') + '?search=UniqueTitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('UniqueTitle' in t['title'] for t in response.data))

    def test_filter_and_search_results_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        t1 = create_ticket(tenant=other_tenant, created_by=self.user)
        t1.title = 'OtherTenantTitle'
        t1.status = 'open'
        t1.priority = 'high'
        t1.save()
        t2 = create_ticket(tenant=self.tenant, created_by=self.user)
        t2.title = 'MyTenantTitle'
        t2.status = 'open'
        t2.priority = 'high'
        t2.save()
        url = reverse('engagements:ticket-list') + '?status=open&priority=high&search=MyTenantTitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for ticket in response.data:
            self.assertEqual(ticket['tenant'], self.tenant.id)
            self.assertIn('MyTenantTitle', ticket['title'])
