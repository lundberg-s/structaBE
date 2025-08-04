from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from engagements.tests.test_helper import EngagementsTestHelper
from engagements.tests.test_constants import (
    TestURLs,
    TestData,
    QueryParams,
    ExpectedResults,
    SetupDefaults,
    WorkItemType,
)
from engagements.models import Attachment


class TestAttachmentFlow(EngagementsTestHelper):
    def setUp(self):
        super().setUp()
        self.tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        self.user = self.create_user(tenant=self.tenant)
        self.token = self.authenticate_user()
        self.authenticate_client()
        self.tickets = self.create_tickets(amount=SetupDefaults.WORK_ITEM_AMOUNT)
        self.ticket = self.tickets[0]
        self.attachments = self.create_attachments(self.ticket, amount=SetupDefaults.ATTACHMENT_AMOUNT)
        self.attachment = self.attachments[0]

    def test_create_attachment_returns_201(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        response = self.client.post(url, attachment_data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_create_attachment_returns_id(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        response = self.client.post(url, attachment_data, format="multipart")
        self.assertIn("id", response.data)

    def test_create_attachment_sets_created_by(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        response = self.client.post(url, attachment_data, format="multipart")
        attachment = Attachment.objects.get(id=response.data["id"])
        self.assertEqual(attachment.created_by, self.user.id)

    def test_create_attachment_sets_tenant(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        response = self.client.post(url, attachment_data, format="multipart")
        attachment = Attachment.objects.get(id=response.data["id"])
        self.assertEqual(attachment.tenant, self.tenant)

    def test_create_attachment_invalid_work_item_returns_400(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data(work_item=999999)
        response = self.client.post(url, attachment_data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_attachment(self):
        # Clear authentication
        self.client.cookies.clear()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        response = self.client.post(url, attachment_data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_list_attachments_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_attachments_returns_correct_count(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), ExpectedResults.RESULT_COUNT
        )  # 3 attachments from setUp

    def test_list_attachments_scoped_to_tenant(self):
        self.authenticate_client()
        # Create attachment for other tenant
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(amount=1, tenant=other_tenant, user=other_user)
        self.create_attachments(other_tickets[0], amount=1, tenant=other_tenant, user=other_user)

        url = reverse(TestURLs.ATTACHMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), ExpectedResults.RESULT_COUNT
        )  # Only current tenant attachments

    def test_retrieve_attachment_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_attachment_returns_correct_id(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        response = self.client.get(url)
        self.assertEqual(str(response.data["id"]), str(self.attachment.id))

    def test_retrieve_other_tenant_attachment_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_attachments = self.create_attachments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_attachment = other_attachments[0]

        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[other_attachment.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_attachment_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        data = {"filename": "Updated filename.txt"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_attachment_changes_filename(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        data = {"filename": "Updated filename.txt"}
        self.client.patch(url, data, format="json")
        self.attachment.refresh_from_db()
        self.assertEqual(self.attachment.filename, "Updated filename.txt")

    def test_update_other_tenant_attachment_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_attachments = self.create_attachments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_attachment = other_attachments[0]

        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[other_attachment.id])
        data = {"filename": "Hacked filename.txt"}
        response = self.client.patch(url, data, format="json")
        self.assertIn(response.status_code, (403, 404))

    def test_update_protected_fields_ignored(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
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
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        data = {
            "created_by": self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            "tenant": self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        }
        self.client.patch(url, data, format="json")
        self.attachment.refresh_from_db()
        self.assertEqual(self.attachment.created_by, self.user.id)

    def test_delete_attachment_returns_204(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_attachment_removes_from_database(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        self.client.delete(url)
        
        # Attachment should be hard deleted from database
        with self.assertRaises(Attachment.DoesNotExist):
            self.attachment.refresh_from_db()

    def test_delete_attachment_removes_from_list(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        self.client.delete(url)

        list_url = reverse(TestURLs.ATTACHMENT_LIST)
        list_response = self.client.get(list_url)
        self.assertFalse(
            any(j["id"] == str(self.attachment.id) for j in list_response.data)
        )

    def test_delete_attachment_returns_404_on_detail(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        self.client.delete(url)

        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_other_tenant_attachment_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_attachments = self.create_attachments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_attachment = other_attachments[0]

        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[other_attachment.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))

    def test_delete_other_tenant_attachment_preserves_record(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_attachments = self.create_attachments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_attachment = other_attachments[0]

        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[other_attachment.id])
        self.client.delete(url)
        self.assertTrue(Attachment.objects.filter(id=other_attachment.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        data = {"created_at": TestData.FAKE_CREATED_AT}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_protected_fields_not_modified(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_DETAIL, args=[self.attachment.id])
        data = {"created_at": TestData.FAKE_CREATED_AT}
        self.client.patch(url, data, format="json")
        self.attachment.refresh_from_db()
        self.assertNotEqual(str(self.attachment.created_at), TestData.FAKE_CREATED_AT)

    def test_create_protected_fields_ignored(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        attachment_data.update({
            'created_by': self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            'tenant': self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        })
        response = self.client.post(url, attachment_data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_create_protected_fields_not_set(self):
        self.authenticate_client()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        attachment_data = self.get_attachment_data()
        attachment_data.update({
            'created_by': self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            'tenant': self.create_tenant(work_item_type=WorkItemType.TICKET).id,
        })
        response = self.client.post(url, attachment_data, format="multipart")
        attachment = self.get_attachment(response.data["id"])
        self.assertEqual(attachment.created_by, self.user.id)

    def test_unauthenticated_user_denied_list(self):
        # Clear authentication
        self.client.cookies.clear()
        url = reverse(TestURLs.ATTACHMENT_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_search_returns_200(self):
        self.authenticate_client()
        self.attachment.filename = TestData.UNIQUE_TITLE
        self.attachment.save()

        url = self.build_search_url(
            reverse(TestURLs.ATTACHMENT_LIST), TestData.UNIQUE_TITLE
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_finds_matching_filename(self):
        self.authenticate_client()
        self.attachment.filename = TestData.UNIQUE_TITLE
        self.attachment.save()

        url = self.build_search_url(
            reverse(TestURLs.ATTACHMENT_LIST), TestData.UNIQUE_TITLE
        )
        response = self.client.get(url)
        self.assertTrue(any(TestData.UNIQUE_TITLE in j["filename"] for j in response.data))

    def test_search_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )

        other_tickets = self.create_tickets(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_attachments = self.create_attachments(
            other_tickets[0], amount=1, tenant=other_tenant, user=other_user
        )
        other_attachment = other_attachments[0]
        other_attachment.filename = TestData.OTHER_TENANT_TITLE
        other_attachment.save()

        self.attachment.filename = TestData.MY_TENANT_TITLE
        self.attachment.save()

        url = self.build_search_url(
            reverse(TestURLs.ATTACHMENT_LIST),
            TestData.MY_TENANT_TITLE,
        )

        response = self.client.get(url)
        for attachment in response.data:
            self.assertEqual(attachment["tenant"], self.tenant.id)

    def get_attachment_data(self, **kwargs):
        """Helper method to create attachment data for testing."""
        file = SimpleUploadedFile(
            "test_file.txt",
            b"test content",
            content_type="text/plain"
        )
        
        data = {
            'work_item': kwargs.get('work_item', self.ticket.id),
            'file': file,
            'filename': kwargs.get('filename', 'test_file.txt'),
        }
        
        return data
