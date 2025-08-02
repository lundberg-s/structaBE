from django.urls import reverse
from rest_framework.test import APITestCase
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_job, create_default_status, create_default_priority, create_default_category
from engagements.tests.client.test_base import JobTenancySetup
from engagements.models import Job
from datetime import timedelta
from django.utils import timezone


class TestJobFlow(JobTenancySetup, APITestCase):
    def setUp(self):
        super().setUp()
        self.job_data = {
            "title": "Test Job",
            "description": "A test job",
            "status": self.status.id,
            "category": self.category.id,
            "priority": self.priority.id,
            "deadline": (timezone.now() + timedelta(days=7)).isoformat(),
            "estimated_hours": "10.5",
        }

    def test_create_job_success(self):
        self.authenticate_client()
        url = reverse("engagements:job-list")
        response = self.client.post(url, self.job_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_create_job_auto_sets_user_and_tenant(self):
        self.authenticate_client()
        other_user = create_user(
            tenant=self.tenant, username="otheruser", password="otherpass"
        )
        other_tenant = create_tenant()
        url = reverse("engagements:job-list")
        data = self.job_data.copy()
        data["created_by"] = other_user.id
        data["tenant"] = other_tenant.id
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        job = Job.objects.get(id=response.data["id"])
        self.assertEqual(job.created_by, self.user)
        self.assertEqual(job.tenant, self.tenant)

    def test_create_job_invalid_foreign_key(self):
        self.authenticate_client()
        url = reverse("engagements:job-list")
        # Invalid category
        data = self.job_data.copy()
        data["category"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        # Invalid status
        data = self.job_data.copy()
        data["status"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_job(self):
        url = reverse("engagements:job-list")
        response = self.client.post(url, self.job_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_list_jobs_for_user_tenant_only(self):
        self.authenticate_client()
        # Create job for another tenant
        other_tenant = create_tenant()
        create_job(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for job in response.data:
            self.assertEqual(job["tenant"], self.tenant.id)

    def test_retrieve_job_from_same_tenant(self):
        self.authenticate_client()
        job = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["id"]), str(job.id))

    def test_retrieve_job_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        job = create_job(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_job_success(self):
        self.authenticate_client()
        job = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.title, "Updated Title")

    def test_update_job_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        job = create_job(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        data = {"title": "Hacked"}
        response = self.client.patch(url, data, format="json")
        self.assertIn(response.status_code, (403, 404))

    def test_cannot_spoof_protected_fields_on_update(self):
        self.authenticate_client()
        job = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        data = {
            "created_by": create_user(
                tenant=self.tenant, username="spoof", password="pass"
            ).id,
            "tenant": create_tenant().id,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.created_by, self.user)
        self.assertEqual(job.tenant, self.tenant)

    def test_delete_own_job_success(self):
        self.authenticate_client()
        job = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        job.refresh_from_db()
        self.assertTrue(job.is_deleted)
        # Optionally check not in list or detail
        list_url = reverse("engagements:job-list")
        list_response = self.client.get(list_url)
        self.assertFalse(any(j["id"] == str(job.id) for j in list_response.data))
        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_job_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        job = create_job(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Job.objects.filter(id=job.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        job = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-detail", args=[job.id])
        data = {"created_at": "2000-01-01T00:00:00Z"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertNotEqual(str(job.created_at), "2000-01-01T00:00:00Z")

    def test_cannot_spoof_protected_fields_on_create(self):
        self.authenticate_client()
        url = reverse("engagements:job-list")
        data = self.job_data.copy()
        data["created_by"] = create_user(
            tenant=self.tenant, username="spoof", password="pass"
        ).id
        data["tenant"] = create_tenant().id
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        job = Job.objects.get(id=response.data["id"])
        self.assertEqual(job.created_by, self.user)
        self.assertEqual(job.tenant, self.tenant)

    def test_create_job_success_status_code(self):
        self.authenticate_client()
        url = reverse("engagements:job-list")
        response = self.client.post(url, self.job_data, format="json")
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            print(f"Request data: {self.job_data}")
            input("Press Enter to continue...")
        self.assertEqual(response.status_code, 201)

    def test_create_job_invalid_category_status_code(self):
        self.authenticate_client()
        url = reverse("engagements:job-list")
        data = self.job_data.copy()
        data["category"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_job_unauthenticated_status_code(self):
        url = reverse("engagements:job-list")
        response = self.client.post(url, self.job_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_denied_status_code(self):
        url = reverse("engagements:job-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_jobs_by_status(self):
        self.authenticate_client()
        other_status = create_default_status(
            tenant=self.tenant, label="Closed", created_by=self.user
        )
        another_status = create_default_status(
            tenant=self.tenant, label="Open", created_by=self.user
        )

        create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=other_status,
            category=self.category,
            priority=self.priority,
        )
        create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=another_status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:job-list")
        response = self.client.get(url, {"status__label": "Closed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_search_jobs_by_title_or_description(self):
        self.authenticate_client()
        j = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        j.title = "UniqueTitle"
        j.description = "SpecialDesc"
        j.save()
        url = reverse("engagements:job-list") + "?search=UniqueTitle"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("UniqueTitle" in j["title"] for j in response.data))

    def test_filter_and_search_results_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        j1 = create_job(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        j1.title = "OtherTenantTitle"
        j1.status = self.status
        j1.priority = self.priority
        j1.save()
        j2 = create_job(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        j2.title = "MyTenantTitle"
        j2.status = self.status
        j2.priority = self.priority
        j2.save()
        url = (
            reverse("engagements:job-list")
            + "?status=open&priority=high&search=MyTenantTitle"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for job in response.data:
            self.assertEqual(job["tenant"], self.tenant.id)
            self.assertIn("MyTenantTitle", job["title"])
