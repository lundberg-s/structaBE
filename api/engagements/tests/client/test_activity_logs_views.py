from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_ticket, create_job, create_case, create_comment, create_attachment, create_assignment
from engagements.models import ActivityLog, Ticket, Job, Case, Comment, Attachment, Assignment
from engagements.tests.client.test_base import FullySetupTest
from django.core.files.uploadedfile import SimpleUploadedFile

class TestActivityLogFlow(FullySetupTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.work_item = self.ticket
        self.user2 = create_user(tenant=self.tenant, username='user2', email='user2@example.com')

    def authenticate(self):
        self.authenticate_client()

    def test_activitylog_created_for_ticket_crud(self):
        self.authenticate()
        # Create
        url = reverse('engagements:ticket-list')
        data = {
            'title': 'Log Ticket',
            'description': 'Log test',
            'status': 'open',
            'category': 'ticket',
            'priority': 'medium',
            'deadline': None,
            'ticket_number': 'T-LOG',   
            'urgency': 'medium',
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        ticket_id = response.data['id']
        log = ActivityLog.objects.filter(work_item_id=ticket_id, activity_type='created').first()
        self.assertIsNotNone(log)
        # Update
        url = reverse('engagements:ticket-detail', args=[ticket_id])
        response = self.client.patch(url, {'title': 'Updated Log Ticket'}, format='json')
        self.assertEqual(response.status_code, 200)
        log = ActivityLog.objects.filter(work_item_id=ticket_id, activity_type='updated').first()
        self.assertIsNotNone(log)
        # Delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        log = ActivityLog.objects.filter(work_item_id=ticket_id, activity_type='deleted').first()
        self.assertIsNotNone(log)

    def test_activitylog_created_for_comment_crud(self):
        self.authenticate()
        # Create
        url = reverse('engagements:comment-list')
        response = self.client.post(url, {'content': 'Log comment', 'work_item': self.work_item.id}, format='json')
        self.assertIn(response.status_code, (200, 201))
        comment_id = response.data['id']
        comment = Comment.objects.get(id=comment_id)
        log = ActivityLog.objects.filter(work_item=comment.work_item, activity_type='commented').first()
        self.assertIsNotNone(log)
        # Update
        url = reverse('engagements:comment-detail', args=[comment_id])
        response = self.client.patch(url, {'content': 'Updated log comment'}, format='json')
        self.assertEqual(response.status_code, 200)
        log = ActivityLog.objects.filter(work_item=comment.work_item, activity_type='updated').first()
        self.assertIsNotNone(log)
        # Delete
        response = self.client.delete(url)
        self.assertIn(response.status_code, (204, 200, 202))
        log = ActivityLog.objects.filter(work_item=comment.work_item, activity_type='deleted').first()
        self.assertIsNotNone(log)

    def test_activitylog_created_for_attachment_crud(self):
        self.authenticate()
        # Create
        url = reverse('engagements:attachment-list')
        file = SimpleUploadedFile('logfile.txt', b'logcontent', content_type='text/plain')
        data = {
            'work_item': str(self.work_item.id),
            'filename': 'logfile.txt',
            'file': file,
            'file_size': 10,
            'mime_type': 'text/plain',
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, (200, 201))
        attachment_id = response.data['id']
        attachment = Attachment.objects.get(id=attachment_id)
        log = ActivityLog.objects.filter(work_item=attachment.work_item, activity_type='attachment_added').first()
        self.assertIsNotNone(log)
        # Update
        url = reverse('engagements:attachment-detail', args=[attachment_id])
        response = self.client.patch(url, {'filename': 'logfile2.txt'}, format='json')
        self.assertEqual(response.status_code, 200)
        log = ActivityLog.objects.filter(work_item=attachment.work_item, activity_type='attachment_updated').first()
        self.assertIsNotNone(log)
        # Delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        log = ActivityLog.objects.filter(work_item=attachment.work_item, activity_type='attachment_deleted').first()
        self.assertIsNotNone(log)

    def test_activitylog_created_for_assignment_create(self):
        self.authenticate()
        url = reverse('engagements:assignment-create')
        assignee = create_user(tenant=self.tenant, username='assignee2', email='assignee2@example.com')
        data = {
            'work_item': str(self.work_item.id),
            'user': assignee.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        assignment = Assignment.objects.get(id=response.data['id'])
        log = ActivityLog.objects.filter(work_item=assignment.work_item, activity_type='assigned').first()
        self.assertIsNotNone(log)
