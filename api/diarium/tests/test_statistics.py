from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from diarium.tests.factory import create_tenant, create_user, create_ticket
from diarium.models import Ticket

class StatisticsViewTests(APITestCase):
    def setUp(self):
        self.tenant = create_tenant('TenantA')
        self.user = create_user(self.tenant, username='userA', password='passA')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tenant.workitem_type = 'ticket'
        self.tenant.save()

    def test_ticket_statistics(self):
        # Create some tickets
        create_ticket(self.tenant, self.user, title='Open Ticket', status='open')
        create_ticket(self.tenant, self.user, title='Closed Ticket', status='closed')
        url = reverse('workitem-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # type: ignore
        stats = response.data['ticket']  # type: ignore
        self.assertEqual(stats['total'], 2)
        self.assertIn('by_status', stats)
        self.assertTrue('open' in stats['by_status'] or 'closed' in stats['by_status']) 