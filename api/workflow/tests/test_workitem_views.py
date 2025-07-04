from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from workflow.tests.factory import create_tenant, create_user, create_work_item, create_comment, create_attachment
from workflow.models import Ticket, Comment, Attachment
import uuid

class WorkItemViewTests(APITestCase):
    def setUp(self):
        self.tenant = create_tenant('TenantA')
        self.user = create_user(self.tenant, username='userA', password='passA')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Set tenant to use tickets
        self.tenant.work_item_type = 'ticket'
        self.tenant.save()

    def test_create_and_fetch_ticket_with_comment_and_attachment(self):
        # Create work_item
        work_item = create_work_item(self.tenant, self.user, title='My First Item', status='open')

        # Attach a comment
        comment = create_comment(work_item, self.user, content='A test comment')
        # Attach a file
        attachment = create_attachment(work_item, self.user, filename='test.txt', content=b'hello world')

        # Fetch ticket detail
        response = self.client.get(reverse('workflow:current-work_item-detail', kwargs={'pk': work_item.id}))
        self.assertEqual(response.status_code, 200)  # type: ignore
        data = response.data  # type: ignore

        print("\nWorkItem detail response:", data)
        self.assertEqual(data['title'], 'My First Item')
        # Check comments
        self.assertTrue(any(c['content'] == 'A test comment' for c in data.get('comments', [])))
        # Check attachments
        self.assertTrue(any(a['filename'] == 'test.txt' for a in data.get('attachments', [])))

    def test_filtering_and_search(self):
        # Create tickets
        t1 = create_work_item(self.tenant, self.user, title='Alpha Ticket', status='open')
        t2 = create_work_item(self.tenant, self.user, title='Beta Ticket', status='closed')
        # Filter by status
        response = self.client.get(reverse('workflow:current-work_item-list'), {'status': 'open'})
        self.assertEqual(response.status_code, 200)  # type: ignore
        self.assertTrue(any(t['title'] == 'Alpha Ticket' for t in response.data))  # type: ignore
        self.assertFalse(any(t['title'] == 'Beta Ticket' for t in response.data))  # type: ignore
        # Search by title
        response = self.client.get(reverse('workflow:current-work_item-list'), {'search': 'Beta'})
        self.assertEqual(response.status_code, 200)  # type: ignore
        self.assertTrue(any(t['title'] == 'Beta Ticket' for t in response.data))  # type: ignore
        self.assertFalse(any(t['title'] == 'Alpha Ticket' for t in response.data))  # type: ignore 