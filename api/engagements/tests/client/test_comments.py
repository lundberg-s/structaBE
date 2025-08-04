from django.urls import reverse

from engagements.tests.test_helper import EngagementsTestHelper
from engagements.tests.test_constants import (
    TestURLs,
    TestData,
    QueryParams,
    ExpectedResults,
    SetupDefaults,
    WorkItemType,
)
from engagements.models import Comment


class TestCommentFlow(EngagementsTestHelper):
    def setUp(self):
        super().setUp()
        self.tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        self.user = self.create_user(tenant=self.tenant)
        self.token = self.authenticate_user()
        self.authenticate_client()
        self.tickets = self.create_tickets(amount=SetupDefaults.WORK_ITEM_AMOUNT)
        self.ticket = self.tickets[0]
        self.comments = self.create_comments(self.ticket, amount=SetupDefaults.WORK_ITEM_AMOUNT)
        self.comment = self.comments[0]

    def test_create_comment_returns_201(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, comment_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_comment_returns_id(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, comment_data, format="json")
        self.assertIn("id", response.data)

    def test_create_comment_sets_created_by(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, comment_data, format="json")
        comment = Comment.objects.get(id=response.data["id"])
        self.assertEqual(comment.created_by, self.user.id)

    def test_create_comment_sets_tenant(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, comment_data, format="json")
        comment = Comment.objects.get(id=response.data["id"])
        self.assertEqual(comment.tenant, self.tenant)

    def test_create_comment_invalid_work_item_returns_400(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': 999999,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, comment_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_comment(self):
        # Clear authentication
        self.client.cookies.clear()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment'
        }
        response = self.client.post(url, comment_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_list_comments_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_comments_returns_correct_count(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), ExpectedResults.RESULT_COUNT
        )  # 3 comments from setUp

    def test_list_comments_scoped_to_tenant(self):
        self.authenticate_client()
        # Create comment for other tenant
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(amount=1, tenant=other_tenant, user=other_user)
        self.create_comments(other_tickets[0], amount=1, tenant=other_tenant, user=other_user)

        url = reverse(TestURLs.COMMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), ExpectedResults.RESULT_COUNT
        )  # Only current tenant comments

    def test_retrieve_comment_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_comment_returns_correct_id(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(str(response.data["id"]), str(self.comment.id))

    def test_retrieve_other_tenant_comment_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_comments = self.create_comments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_comment = other_comments[0]

        url = reverse(TestURLs.COMMENT_DETAIL, args=[other_comment.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_comment_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        data = {"content": "Updated comment content"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_comment_changes_content(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        data = {"content": "Updated comment content"}
        self.client.patch(url, data, format="json")
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated comment content")

    def test_update_other_tenant_comment_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_comments = self.create_comments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_comment = other_comments[0]

        url = reverse(TestURLs.COMMENT_DETAIL, args=[other_comment.id])
        data = {"content": "Hacked comment"}
        response = self.client.patch(url, data, format="json")
        self.assertIn(response.status_code, (403, 404))

    def test_update_protected_fields_ignored(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        data = {
            "created_by": self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            "tenant": self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_protected_fields_not_changed(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        data = {
            "created_by": self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            "tenant": self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        }
        self.client.patch(url, data, format="json")
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.created_by, self.user.id)

    def test_delete_comment_returns_204(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_comment_removes_from_database(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        self.client.delete(url)
        
        # Comment should be hard deleted from database
        with self.assertRaises(Comment.DoesNotExist):
            self.comment.refresh_from_db()

    def test_delete_comment_removes_from_list(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        self.client.delete(url)

        list_url = reverse(TestURLs.COMMENT_LIST)
        list_response = self.client.get(list_url)
        self.assertFalse(
            any(j["id"] == str(self.comment.id) for j in list_response.data)
        )

    def test_delete_comment_returns_404_on_detail(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        self.client.delete(url)

        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_other_tenant_comment_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_comments = self.create_comments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_comment = other_comments[0]

        url = reverse(TestURLs.COMMENT_DETAIL, args=[other_comment.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))

    def test_delete_other_tenant_comment_preserves_record(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_comments = self.create_comments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_comment = other_comments[0]

        url = reverse(TestURLs.COMMENT_DETAIL, args=[other_comment.id])
        self.client.delete(url)
        self.assertTrue(Comment.objects.filter(id=other_comment.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        data = {"created_at": TestData.FAKE_CREATED_AT}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_protected_fields_not_modified(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_DETAIL, args=[self.comment.id])
        data = {"created_at": TestData.FAKE_CREATED_AT}
        self.client.patch(url, data, format="json")
        self.comment.refresh_from_db()
        self.assertNotEqual(str(self.comment.created_at), TestData.FAKE_CREATED_AT)

    def test_create_protected_fields_ignored(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment',
            'created_by': self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            'tenant': self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        }
        response = self.client.post(url, comment_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_protected_fields_not_set(self):
        self.authenticate_client()
        url = reverse(TestURLs.COMMENT_LIST)
        comment_data = {
            'work_item': self.ticket.id,
            'content': 'This is a test comment',
            'created_by': self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            'tenant': self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        }
        response = self.client.post(url, comment_data, format="json")
        comment = self.get_comment(response.data["id"])
        self.assertEqual(comment.created_by, self.user.id)

    def test_unauthenticated_user_denied_list(self):
        # Clear authentication
        self.client.cookies.clear()
        url = reverse(TestURLs.COMMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_search_returns_200(self):
        self.authenticate_client()
        self.comment.content = TestData.UNIQUE_TITLE
        self.comment.save()

        url = self.build_search_url(
            reverse(TestURLs.COMMENT_LIST), TestData.UNIQUE_TITLE
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_finds_matching_content(self):
        self.authenticate_client()
        self.comment.content = TestData.UNIQUE_TITLE
        self.comment.save()

        url = self.build_search_url(
            reverse(TestURLs.COMMENT_LIST), TestData.UNIQUE_TITLE
        )
        response = self.client.get(url)
        self.assertTrue(any(TestData.UNIQUE_TITLE in j["content"] for j in response.data))

    def test_search_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )

        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_comments = self.create_comments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_comment = other_comments[0]
        other_comment.content = TestData.OTHER_TENANT_TITLE
        other_comment.save()

        self.comment.content = TestData.MY_TENANT_TITLE
        self.comment.save()

        url = self.build_search_url(
            reverse(TestURLs.COMMENT_LIST),
            TestData.MY_TENANT_TITLE,
        )

        response = self.client.get(url)
        for comment in response.data:
            self.assertEqual(comment["tenant"], self.tenant.id)
