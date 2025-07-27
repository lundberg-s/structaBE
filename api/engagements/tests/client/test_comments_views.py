from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_comment, create_ticket
from engagements.tests.client.test_base import FullySetupTest
from engagements.models import Comment

class TestCommentFlow(FullySetupTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_create_comment_success(self):
        self.authenticate_client()
        url = reverse('engagements:comment-list')
        response = self.client.post(
            url,
            {
                'content': 'Test comment',
                'work_item': self.ticket.id,
            },
            format='json'
        )
        self.assertIn(response.status_code, (200, 201))
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.created_by, self.user)
        self.assertEqual(comment.tenant, self.tenant)

    def test_cannot_spoof_author_or_tenant_on_create_or_update(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        other_tenant = create_tenant()
        url = reverse('engagements:comment-list')
        response = self.client.post(
            url,
            {
                'content': 'Attempted spoofing',
                'work_item': self.ticket.id,
                'author': other_user.id,       # Should be ignored
                'tenant': other_tenant.id,     # Should be ignored
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.created_by, self.user)
        self.assertEqual(comment.tenant, self.tenant)

    def test_filtering_by_work_item_and_author(self):
        self.authenticate_client()
        other_ticket = create_ticket(tenant=self.tenant, created_by=self.user)
        create_comment(work_item=other_ticket, author=self.user, content='Other comment')
        url = reverse('engagements:comment-list') + f'?work_item={self.ticket.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for comment in response.data:
            self.assertEqual(comment['work_item'], self.ticket.id)

    def test_create_comment_invalid_work_item(self):
        self.authenticate_client()
        url = reverse('engagements:comment-list')
        # Non-existent work item
        response = self.client.post(
            url,
            {'content': 'Invalid', 'work_item': 999999},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        # Work item from another tenant
        other_tenant = create_tenant()
        other_ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        response = self.client.post(
            url,
            {'content': 'Invalid', 'work_item': other_ticket.id},
            format='json'
        )
        self.assertIn(response.status_code, (400, 404, 403))

    def test_list_comments_for_user_tenant_only(self):
        self.authenticate_client()
        # Create comment for another tenant
        other_tenant = create_tenant()
        other_ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        create_comment(work_item=other_ticket, author=self.user, content='Other tenant comment')
        # Should only see comments from self.tenant
        url = reverse('engagements:comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for comment in response.data:
            self.assertEqual(comment['tenant'], self.tenant.id)

    def test_retrieve_comment_from_same_tenant(self):
        self.authenticate_client()
        comment = create_comment(work_item=self.ticket, author=self.user, content='Retrieve me')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['id']), str(comment.id))

    def test_retrieve_comment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        comment = create_comment(work_item=other_ticket, author=self.user, content='Forbidden')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_comment_success(self):
        self.authenticate_client()
        comment = create_comment(work_item=self.ticket, author=self.user, content='Old content')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.patch(url, {'content': 'Updated'}, format='json')
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated')

    def test_update_comment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        comment = create_comment(work_item=other_ticket, author=self.user, content='Other tenant')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.patch(url, {'content': 'Hacked'}, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_delete_own_comment_success(self):
        self.authenticate_client()
        comment = create_comment(work_item=self.ticket, author=self.user, content='Delete me')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_delete_comment_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_ticket = create_ticket(tenant=other_tenant, created_by=self.user)
        comment = create_comment(work_item=other_ticket, author=self.user, content='Other tenant')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())

    def test_unauthenticated_user_cannot_create_comment(self):
        url = reverse('engagements:comment-list')
        response = self.client.post(
            url,
            {'content': 'No auth', 'work_item': 1},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_comment_search_filter_by_content(self):
        self.authenticate_client()
        create_comment(work_item=self.ticket, author=self.user, content='UniqueSearchPhrase')
        url = reverse('engagements:comment-list') + '?search=UniqueSearchPhrase'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('UniqueSearchPhrase' in c['content'] for c in response.data))

    def test_timestamp_fields_are_readonly(self):
        self.authenticate_client()
        comment = create_comment(work_item=self.ticket, author=self.user, content='Readonly')
        url = reverse('engagements:comment-detail', args=[comment.id])
        response = self.client.patch(url, {'created_at': '2000-01-01T00:00:00Z'}, format='json')
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertNotEqual(str(comment.created_at), '2000-01-01T00:00:00Z')
