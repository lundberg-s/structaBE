from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from workflow.tests.factory import create_tenant, create_user, create_ticket
from workflow.models import Ticket, ActivityLog

class ActivityLogViewTests(APITestCase):
    def setUp(self):
        self.tenant = create_tenant('TenantA')
        self.user = create_user(self.tenant, username='userA', password='passA')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tenant.work_item_type = 'ticket'
        self.tenant.save()
        self.ticket = create_ticket(self.tenant, self.user, title='Log Ticket')

    def test_create_activity_log(self):
        url = reverse('activity-log-list-create')
        data = {
            'work_item': str(self.ticket.id),
            'user': self.user.id,
            'activity_type': 'created',
            'description': 'Ticket created'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)  # type: ignore
        self.assertEqual(response.data['activity_type'], 'created')  # type: ignore
        self.assertEqual(response.data['description'], 'Ticket created')  # type: ignore

    def test_list_activity_logs(self):
        ActivityLog.objects.create(
            tenant=self.tenant,
            work_item=self.ticket,
            user=self.user,
            activity_type='created',
            description='Ticket created'
        )
        url = reverse('activity-log-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # type: ignore
        self.assertTrue(any(log['description'] == 'Ticket created' for log in response.data))  # type: ignore

    def test_activity_log_list_unauthenticated(self):
        url = reverse('workflow:activity-log-list-create')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_activity_log_retrieve_not_found(self):
        url = reverse('workflow:activity-log-detail', kwargs={'id': '00000000-0000-0000-0000-000000000000'})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_activity_log_create_invalid_data(self):
        url = reverse('activity-log-list-create')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activity_log_filter_by_work_item_user_activity_type(self):
        log1 = ActivityLog.objects.create(
            tenant=self.tenant,
            work_item=self.ticket,
            user=self.user,
            activity_type='created',
            description='desc1'
        )
        log2 = ActivityLog.objects.create(
            tenant=self.tenant,
            work_item=self.ticket,
            user=self.user,
            activity_type='updated',
            description='desc2'
        )
        url = reverse('activity-log-list-create')
        # Filter by work_item
        response = self.client.get(url, {'work_item': str(self.ticket.id)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(str(item['work_item']) == str(self.ticket.id) for item in response.data))
        # Filter by user
        response = self.client.get(url, {'user': self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(str(item['user']['id']) == str(self.user.id) for item in response.data))
        # Filter by activity_type
        response = self.client.get(url, {'activity_type': 'created'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(item['activity_type'] == 'created' for item in response.data))

    def test_activity_log_search_by_description(self):
        ActivityLog.objects.create(
            tenant=self.tenant,
            work_item=self.ticket,
            user=self.user,
            activity_type='created',
            description='unique_search_term'
        )
        url = reverse('activity-log-list-create')
        response = self.client.get(url, {'search': 'unique_search_term'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('unique_search_term' in item['description'] for item in response.data))

    def test_invalid_uuid_returns_400(self):
        url = reverse('activity-log-list-create')
        response = self.client.get(url, {'work_item': 'not-a-uuid'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_nonexistent_uuid_returns_200_and_empty_list(self):
        import uuid
        url = reverse('activity-log-list-create')
        response = self.client.get(url, {'work_item': str(uuid.uuid4())})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_nonexistent_user_returns_200_and_empty_list(self):
        url = reverse('activity-log-list-create')
        response = self.client.get(url, {'user': 999999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_invalid_activity_type_returns_200_and_empty_list(self):
        url = reverse('activity-log-list-create')
        response = self.client.get(url, {'activity_type': 'not-a-type'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_activity_log_retrieve_existing(self):
        log = ActivityLog.objects.create(
            tenant=self.tenant,
            work_item=self.ticket,
            user=self.user,
            activity_type='created',
            description='desc'
        )
        url = reverse('activity-log-detail', kwargs={'id': log.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(log.id)) 