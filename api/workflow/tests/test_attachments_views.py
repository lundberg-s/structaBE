from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from workflow.tests.factory import create_tenant, create_user, create_ticket, create_attachment
from workflow.models import Ticket, Attachment

class AttachmentViewTests(APITestCase):
    def setUp(self):
        self.tenant = create_tenant('TenantA')
        self.user = create_user(self.tenant, username='userA', password='passA')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tenant.workitem_type = 'ticket'
        self.tenant.save()
        self.ticket = create_ticket(self.tenant, self.user, title='Attachment Ticket')

    def test_create_attachment(self):
        url = reverse('attachment-list-create')
        file_content = b'hello world'
        data = {
            'workitem': str(self.ticket.id),
            'filename': 'test.txt',
            'file': ('test.txt', file_content, 'text/plain'),
            'file_size': len(file_content),
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)  # type: ignore
        self.assertEqual(response.data['filename'], 'test.txt')  # type: ignore

    def test_list_attachments(self):
        create_attachment(self.ticket, self.user, filename='test.txt', content=b'hello world')
        url = reverse('attachment-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # type: ignore
        self.assertTrue(any(a['filename'] == 'test.txt' for a in response.data))  # type: ignore 