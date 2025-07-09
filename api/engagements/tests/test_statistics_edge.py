from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from engagements.tests.factory import create_tenant, create_user, create_ticket
from engagements.models import Ticket

class StatisticsEdgeCaseTests(APITestCase):
    def setUp(self):
        self.tenant = create_tenant('TenantA')
        self.user = create_user(self.tenant, username='userA', password='passA')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tenant.work_item_type = 'ticket'
        self.tenant.save()

    def test_statistics_no_tickets(self):
        url = reverse('work_item-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # type: ignore
        stats = response.data['ticket']  # type: ignore
        self.assertEqual(stats['total'], 0)

    def test_statistics_all_closed(self):
        create_ticket(self.tenant, self.user, title='Closed Ticket 1', status='closed')
        create_ticket(self.tenant, self.user, title='Closed Ticket 2', status='closed')
        url = reverse('work_item-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # type: ignore
        stats = response.data['ticket']  # type: ignore
        self.assertEqual(stats['total'], 2)
        self.assertIn('closed', stats['by_status']) 