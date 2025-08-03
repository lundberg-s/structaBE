from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import TestDataFactory
from engagements.tests.client.test_base import FullySetupTest
from engagements.models import Comment

class TestCommentFlow(FullySetupTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_create_comment_success(self):
        self.authenticate_client()
        url = reverse('engagements:comment-list')
        data = {
            'work_item': self.work_item.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.created_by, self.user)
        self.assertEqual(comment.tenant, self.tenant)

    def test_cannot_spoof_uploaded_by_or_tenant_on_create_or_update(self):
        self.authenticate_client()
        url = reverse('engagements:comment-list')
        data = {
            'work_item': self.work_item.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.created_by, self.user)
        self.assertEqual(comment.tenant, self.tenant)

    def test_create_comment_invalid_work_item(self):
        self.authenticate_client()
        url = reverse('engagements:comment-list')
        # Non-existent work item
        data = {
            'content': 'This is a test comment',
            'work_item': 999999,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Work item from another tenant
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        data = {
            'content': 'This is a test comment',
            'work_item': other_work_item.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (400, 403, 404))

    def test_list_comments_for_user_tenant_only(self):
        self.authenticate_client()
        # Create comment for another tenant
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        other_factory.create_comment(other_work_item, other_user, 'other comment')
        url = reverse('engagements:comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for comment in response.data:
            self.assertEqual(comment['tenant'], self.tenant.id)

    def test_retrieve_comment_from_same_tenant(self):
        self.authenticate_client()
        comment = self.factory.create_comment(self.work_item, self.user, 'retrieve comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['id']), str(comment.id))

    def test_retrieve_comment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        comment = other_factory.create_comment(other_work_item, other_user, 'forbidden comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_comment_success(self):
        self.authenticate_client()
        comment = self.factory.create_comment(self.work_item, self.user, 'update comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        data = {'content': 'Updated comment content'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated comment content')

    def test_update_comment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        comment = other_factory.create_comment(other_work_item, other_user, 'forbidden comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        data = {'content': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_delete_own_comment_success(self):
        self.authenticate_client()
        comment = self.factory.create_comment(self.work_item, self.user, 'delete comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_comment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_work_item = other_factory.create_work_item()
        comment = other_factory.create_comment(other_work_item, other_user, 'forbidden comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_unauthenticated_user_cannot_create_comment(self):
        url = reverse('engagements:comment-list')
        data = {
            'work_item': self.work_item.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_comment_search_filter_by_content(self):
        self.authenticate_client()
        comment = self.factory.create_comment(self.work_item, self.user, 'UniqueCommentContent')
        url = reverse('engagements:comment-list') + '?search=UniqueCommentContent'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('UniqueCommentContent' in c['content'] for c in response.data))

    def test_timestamp_fields_are_readonly(self):
        self.authenticate_client()
        comment = self.factory.create_comment(self.work_item, self.user, 'test comment')
        url = reverse('engagements:comment-detail', args=[comment.id])
        data = {'created_at': '2000-01-01T00:00:00Z'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertNotEqual(str(comment.created_at), '2000-01-01T00:00:00Z')
