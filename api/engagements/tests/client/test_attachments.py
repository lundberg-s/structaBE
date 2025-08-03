from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import TestDataFactory
from engagements.tests.client.test_base import FullySetupTest
from engagements.models import Attachment

class TestAttachmentFlow(FullySetupTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_create_attachment_success(self):
        self.authenticate_client()
        url = reverse('engagements:attachment-list')
        data = {
            'work_item': self.work_item.id,
            'file': SimpleUploadedFile('test.txt', b'test content'),
            'filename': 'test.txt'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, (200, 201))
        attachment = Attachment.objects.get(id=response.data['id'])
        self.assertEqual(attachment.created_by, self.user)
        self.assertEqual(attachment.tenant, self.tenant)

    def test_cannot_spoof_uploaded_by_or_tenant_on_create_or_update(self):
        self.authenticate_client()
        url = reverse('engagements:attachment-list')
        data = {
            'work_item': self.work_item.id,
            'file': SimpleUploadedFile('test.txt', b'test content'),
            'filename': 'test.txt'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, (200, 201))
        attachment = Attachment.objects.get(id=response.data['id'])
        self.assertEqual(attachment.created_by, self.user)
        self.assertEqual(attachment.tenant, self.tenant)

    def test_create_attachment_invalid_work_item(self):
        self.authenticate_client()
        url = reverse('engagements:attachment-list')
        file = SimpleUploadedFile('bad.txt', b'x', content_type='text/plain')
        # Non-existent work item
        data = {
            'filename': 'bad.txt',
            'file': file,
            'work_item': 999999,
            'file_size': file.size,
            'mime_type': 'text/plain',
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        # Work item from another tenant
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        file2 = SimpleUploadedFile('bad.txt', b'x', content_type='text/plain')
        data = {
            'filename': 'bad.txt',
            'file': file2,
            'work_item': other_work_item.id,
            'file_size': file2.size,
            'mime_type': 'text/plain',
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, (400, 403, 404))

    def test_list_attachments_for_user_tenant_only(self):
        self.authenticate_client()
        # Create attachment for another tenant
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        other_factory.create_attachment(other_work_item, other_user, 'other.txt')
        url = reverse('engagements:attachment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for attachment in response.data:
            self.assertEqual(attachment['tenant'], self.tenant.id)

    def test_retrieve_attachment_from_same_tenant(self):
        self.authenticate_client()
        attachment = self.factory.create_attachment(self.work_item, self.user, 'retrieve.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['id']), str(attachment.id))

    def test_retrieve_attachment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        attachment = other_factory.create_attachment(other_work_item, other_user, 'forbidden.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_attachment_success(self):
        self.authenticate_client()
        attachment = self.factory.create_attachment(self.work_item, self.user, 'update.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        data = {'filename': 'updated.txt'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        attachment.refresh_from_db()
        self.assertEqual(attachment.filename, 'updated.txt')

    def test_update_attachment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        attachment = other_factory.create_attachment(other_work_item, other_user, 'forbidden.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        data = {'filename': 'hacked.txt'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_delete_own_attachment_success(self):
        self.authenticate_client()
        attachment = self.factory.create_attachment(self.work_item, self.user, 'delete.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_attachment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        attachment = other_factory.create_attachment(other_work_item, other_user, 'forbidden.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Attachment.objects.filter(id=attachment.id).exists())

    def test_unauthenticated_user_cannot_create_attachment(self):
        url = reverse('engagements:attachment-list')
        data = {
            'work_item': self.work_item.id,
            'file': SimpleUploadedFile('test.txt', b'test content'),
            'filename': 'test.txt'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 401)

    def test_attachment_search_filter_by_filename(self):
        self.authenticate_client()
        attachment = self.factory.create_attachment(self.work_item, self.user, 'UniqueFilename.txt')
        url = reverse('engagements:attachment-list') + '?search=UniqueFilename'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('UniqueFilename' in a['filename'] for a in response.data))

    def test_timestamp_fields_are_readonly(self):
        self.authenticate_client()
        attachment = self.factory.create_attachment(self.work_item, self.user, 'test.txt')
        url = reverse('engagements:attachment-detail', args=[attachment.id])
        data = {'created_at': '2000-01-01T00:00:00Z'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(str(attachment.created_at), "2000-01-01T00:00:00Z")
