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
from engagements.models import Job


class TestJobFlow(EngagementsTestHelper):
    def setUp(self):
        super().setUp()
        self.tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        self.user = self.create_user(tenant=self.tenant)
        self.token = self.authenticate_user()
        self.authenticate_client()
        self.jobs = self.create_jobs(amount=SetupDefaults.WORK_ITEM_AMOUNT)
        self.job = self.jobs[0]

    def test_create_job_returns_201(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data()
        response = self.client.post(url, job_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_job_returns_id(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data()
        response = self.client.post(url, job_data, format="json")
        self.assertIn("id", response.data)

    def test_create_job_sets_created_by(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data()
        response = self.client.post(url, job_data, format="json")
        job = Job.objects.get(id=response.data["id"])
        self.assertEqual(job.created_by, self.user.id)

    def test_create_job_sets_tenant(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data()
        response = self.client.post(url, job_data, format="json")
        job = Job.objects.get(id=response.data["id"])
        self.assertEqual(job.tenant, self.tenant)

    def test_create_job_invalid_status_returns_400(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data(status=TestData.INVALID_STATUS)
        response = self.client.post(url, job_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_job(self):
        # Clear authentication
        self.client.cookies.clear()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data()
        response = self.client.post(url, job_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_list_jobs_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_jobs_returns_correct_count(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), ExpectedResults.RESULT_COUNT
        )  # 3 jobs from setUp

    def test_list_jobs_scoped_to_tenant(self):
        self.authenticate_client()
        # Create job for other tenant
        other_tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        self.create_jobs(amount=1, tenant=other_tenant, user=other_user)

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), ExpectedResults.RESULT_COUNT
        )  # Only current tenant jobs

    def test_retrieve_job_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_job_returns_correct_id(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        response = self.client.get(url)
        self.assertEqual(str(response.data["id"]), str(self.job.id))

    def test_retrieve_other_tenant_job_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_jobs = self.create_jobs(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_job = other_jobs[0]

        url = reverse(TestURLs.JOB_DETAIL, args=[other_job.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_job_returns_200(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        data = {"title": TestData.UPDATED_TITLE}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_job_changes_title(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        data = {"title": TestData.UPDATED_TITLE}
        self.client.patch(url, data, format="json")
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, TestData.UPDATED_TITLE)

    def test_update_other_tenant_job_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_jobs = self.create_jobs(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_job = other_jobs[0]

        url = reverse(TestURLs.JOB_DETAIL, args=[other_job.id])
        data = {"title": TestData.HACKED_TITLE}
        response = self.client.patch(url, data, format="json")
        self.assertIn(response.status_code, (403, 404))

    def test_update_protected_fields_ignored(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        data = {
            "created_by": self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            "tenant": self.create_tenant(work_item_type=WorkItemType.JOB).id,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_protected_fields_not_changed(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        data = {
            "created_by": self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            "tenant": self.create_tenant(work_item_type=WorkItemType.JOB).id,
        }
        self.client.patch(url, data, format="json")
        self.job.refresh_from_db()
        self.assertEqual(self.job.created_by, self.user.id)

    def test_delete_job_returns_204(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_job_sets_is_deleted(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        self.client.delete(url)
        self.job.refresh_from_db()
        self.assertTrue(self.job.is_deleted)

    def test_delete_job_removes_from_list(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        self.client.delete(url)

        list_url = reverse(TestURLs.JOB_LIST)
        list_response = self.client.get(list_url)
        self.assertFalse(
            any(j["id"] == str(self.job.id) for j in list_response.data)
        )

    def test_delete_job_returns_404_on_detail(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        self.client.delete(url)

        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_other_tenant_job_fails(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_jobs = self.create_jobs(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_job = other_jobs[0]

        url = reverse(TestURLs.JOB_DETAIL, args=[other_job.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))

    def test_delete_other_tenant_job_preserves_record(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )
        other_jobs = self.create_jobs(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_job = other_jobs[0]

        url = reverse(TestURLs.JOB_DETAIL, args=[other_job.id])
        self.client.delete(url)
        self.assertTrue(Job.objects.filter(id=other_job.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        data = {"created_at": TestData.FAKE_CREATED_AT}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_protected_fields_not_modified(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_DETAIL, args=[self.job.id])
        data = {"created_at": TestData.FAKE_CREATED_AT}
        self.client.patch(url, data, format="json")
        self.job.refresh_from_db()
        self.assertNotEqual(str(self.job.created_at), TestData.FAKE_CREATED_AT)

    def test_create_protected_fields_ignored(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data(
            created_by=self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            tenant=self.create_tenant(work_item_type=WorkItemType.JOB).id,
        )
        response = self.client.post(url, job_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_protected_fields_not_set(self):
        self.authenticate_client()
        url = reverse(TestURLs.JOB_LIST)
        job_data = self.get_work_item_data(
            created_by=self.create_user(
                tenant=self.tenant,
                email=TestData.SPOOF_EMAIL,
                password=TestData.SPOOF_PASSWORD,
            ).id,
            tenant=self.create_tenant(work_item_type=WorkItemType.JOB).id,
        )
        response = self.client.post(url, job_data, format="json")
        job = self.get_job(response.data["id"])
        self.assertEqual(job.created_by, self.user.id)

    def test_unauthenticated_user_denied_list(self):
        # Clear authentication
        self.client.cookies.clear()
        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_by_status_returns_200(self):
        self.authenticate_client()
        statuses = self.create_work_item_statuses(amount=2)
        other_status = statuses[0]

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(url, {QueryParams.STATUS_LABEL: other_status.label})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_status_returns_correct_count(self):
        self.authenticate_client()

        unique_status = self.create_work_item_statuses(amount=1)[0]
        unique_status.label = TestData.UNIQUE_STATUS_LABEL
        unique_status.save()

        job_data = self.get_work_item_data(status=unique_status.id)
        self.client.post(reverse(TestURLs.JOB_LIST), job_data, format="json")

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(url, {QueryParams.STATUS_LABEL: unique_status.label})

        self.assertEqual(len(response.data), ExpectedResults.FILTERED_COUNT)

    def test_filter_by_priority_returns_200(self):
        self.authenticate_client()
        priorities = self.create_work_item_priorities(amount=2)
        other_priority = priorities[0]

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(
            url, {QueryParams.PRIORITY_LABEL: other_priority.label}
        )
        self.assertEqual(response.status_code, 200)

    def test_filter_by_priority_returns_correct_count(self):
        self.authenticate_client()

        unique_priority = self.create_work_item_priorities(amount=1)[0]
        unique_priority.label = TestData.UNIQUE_PRIORITY_LABEL
        unique_priority.save()

        job_data = self.get_work_item_data(priority=unique_priority.id)
        self.client.post(reverse(TestURLs.JOB_LIST), job_data, format="json")

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(
            url, {QueryParams.PRIORITY_LABEL: unique_priority.label}
        )

        self.assertEqual(len(response.data), ExpectedResults.FILTERED_COUNT)

    def test_filter_by_category_returns_200(self):
        self.authenticate_client()
        categories = self.create_work_item_categories(amount=2)
        other_category = categories[0]

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(
            url, {QueryParams.CATEGORY_LABEL: other_category.label}
        )
        self.assertEqual(response.status_code, 200)

    def test_filter_by_category_returns_correct_count(self):
        self.authenticate_client()

        unique_category = self.create_work_item_categories(amount=1)[0]
        unique_category.label = TestData.UNIQUE_CATEGORY_LABEL
        unique_category.save()

        job_data = self.get_work_item_data(category=unique_category.id)
        self.client.post(reverse(TestURLs.JOB_LIST), job_data, format="json")

        url = reverse(TestURLs.JOB_LIST)
        response = self.client.get(
            url, {QueryParams.CATEGORY_LABEL: unique_category.label}
        )

        self.assertEqual(len(response.data), ExpectedResults.FILTERED_COUNT)

    def test_search_returns_200(self):
        self.authenticate_client()
        self.job.title = TestData.UNIQUE_TITLE
        self.job.description = TestData.SPECIAL_DESC
        self.job.save()

        url = self.build_search_url(
            reverse(TestURLs.JOB_LIST), TestData.UNIQUE_TITLE
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_finds_matching_title(self):
        self.authenticate_client()
        self.job.title = TestData.UNIQUE_TITLE
        self.job.description = TestData.SPECIAL_DESC
        self.job.save()

        url = self.build_search_url(
            reverse(TestURLs.JOB_LIST), TestData.UNIQUE_TITLE
        )
        response = self.client.get(url)
        self.assertTrue(any(TestData.UNIQUE_TITLE in j["title"] for j in response.data))

    def test_filter_and_search_returns_200(self):
        self.authenticate_client()
        self.job.title = TestData.MY_TENANT_TITLE
        self.job.save()

        url = self.build_filter_url(
            reverse(TestURLs.JOB_LIST),
            status=QueryParams.STATUS_OPEN,
            priority=QueryParams.PRIORITY_HIGH,
            search=TestData.MY_TENANT_TITLE,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter_and_search_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = self.create_tenant(work_item_type=WorkItemType.JOB)
        other_user = self.create_user(
            tenant=other_tenant, email=TestData.OTHER_USER_EMAIL
        )

        other_jobs = self.create_jobs(
            amount=1, tenant=other_tenant, user=other_user
        )
        other_job = other_jobs[0]
        other_job.title = TestData.OTHER_TENANT_TITLE
        other_job.save()

        self.job.title = TestData.MY_TENANT_TITLE
        self.job.save()

        url = self.build_filter_url(
            reverse(TestURLs.JOB_LIST),
            status=QueryParams.STATUS_OPEN,
            priority=QueryParams.PRIORITY_HIGH,
            search=TestData.MY_TENANT_TITLE,
        )

        response = self.client.get(url)
        for job in response.data:
            self.assertEqual(job["tenant"], self.tenant.id)
