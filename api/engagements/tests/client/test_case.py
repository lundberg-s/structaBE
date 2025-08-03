from django.urls import reverse
from rest_framework.test import APITestCase
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import TestDataFactory
from engagements.tests.client.test_base import CaseTenancySetup
from engagements.models import Case
from datetime import timedelta
from django.utils import timezone


class TestCaseFlow(CaseTenancySetup, APITestCase):
    def setUp(self):
        super().setUp()
        self.case_data = self.get_work_item_data()

    def test_create_case_success(self):
        self.authenticate_client()
        url = reverse("engagements:case-list")
        response = self.client.post(url, self.case_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_create_case_auto_sets_user_and_tenant(self):
        self.authenticate_client()
        other_user = create_user(
            tenant=self.tenant, username="otheruser", password="otherpass"
        )
        other_tenant = create_tenant()
        url = reverse("engagements:case-list")
        data = self.case_data.copy()
        data["created_by"] = other_user.id
        data["tenant"] = other_tenant.id
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        case = Case.objects.get(id=response.data["id"])
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_create_case_invalid_foreign_key(self):
        self.authenticate_client()
        url = reverse("engagements:case-list")
        # Invalid category
        data = self.case_data.copy()
        data["category"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        # Invalid status
        data = self.case_data.copy()
        data["status"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_case(self):
        url = reverse("engagements:case-list")
        response = self.client.post(url, self.case_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_list_cases_for_user_tenant_only(self):
        self.authenticate_client()
        # Create case for another tenant
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        other_factory.create_case()
        url = reverse("engagements:case-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case["tenant"], self.tenant.id)

    def test_retrieve_case_from_same_tenant(self):
        self.authenticate_client()
        case = self.factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["id"]), str(case.id))

    def test_retrieve_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        case = other_factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_case_success(self):
        self.authenticate_client()
        case = self.factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.title, "Updated Title")

    def test_update_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        case = other_factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        data = {"title": "Hacked"}
        response = self.client.patch(url, data, format="json")
        self.assertIn(response.status_code, (403, 404))

    def test_cannot_spoof_protected_fields_on_update(self):
        self.authenticate_client()
        case = self.factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        data = {
            "created_by": create_user(
                tenant=self.tenant, username="spoof", password="pass"
            ).id,
            "tenant": create_tenant().id,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_delete_own_case_success(self):
        self.authenticate_client()
        case = self.factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        case.refresh_from_db()
        self.assertTrue(case.is_deleted)
        # Optionally check not in list or detail
        list_url = reverse("engagements:case-list")
        list_response = self.client.get(list_url)
        self.assertFalse(any(c["id"] == str(case.id) for c in list_response.data))
        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        case = other_factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(Case.objects.filter(id=case.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        case = self.factory.create_case()
        url = reverse("engagements:case-detail", args=[case.id])
        data = {"created_at": "2000-01-01T00:00:00Z"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertNotEqual(str(case.created_at), "2000-01-01T00:00:00Z")

    def test_cannot_spoof_protected_fields_on_create(self):
        self.authenticate_client()
        url = reverse("engagements:case-list")
        data = self.case_data.copy()
        data["created_by"] = create_user(
            tenant=self.tenant, username="spoof", password="pass"
        ).id
        data["tenant"] = create_tenant().id
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        case = Case.objects.get(id=response.data["id"])
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_create_case_success_status_code(self):
        self.authenticate_client()
        url = reverse("engagements:case-list")
        response = self.client.post(url, self.case_data, format="json")
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            print(f"Request data: {self.case_data}")
            input("Press Enter to continue...")
        self.assertEqual(response.status_code, 201)

    def test_create_case_invalid_category_status_code(self):
        self.authenticate_client()
        url = reverse("engagements:case-list")
        data = self.case_data.copy()
        data["category"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_case_unauthenticated_status_code(self):
        url = reverse("engagements:case-list")
        response = self.client.post(url, self.case_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_denied_status_code(self):
        url = reverse("engagements:case-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_cases_by_status(self):
        self.authenticate_client()
        other_status = self.factory.create_default_status('Closed')
        another_status = self.factory.create_default_status('Open')

        self.factory.create_case(status=other_status)
        self.factory.create_case(status=another_status)
        url = reverse("engagements:case-list")
        response = self.client.get(url, {"status__label": "Closed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_search_cases_by_title_or_description(self):
        self.authenticate_client()
        case = self.factory.create_case()
        case.title = "UniqueTitle"
        case.description = "SpecialDesc"
        case.save()
        url = reverse("engagements:case-list") + "?search=UniqueTitle"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("UniqueTitle" in c["title"] for c in response.data))

    def test_filter_and_search_results_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)
        other_factory = TestDataFactory(other_tenant, other_user)
        
        c1 = other_factory.create_case()
        c1.title = "OtherTenantTitle"
        c1.save()
        
        c2 = self.factory.create_case()
        c2.title = "MyTenantTitle"
        c2.save()
        
        url = (
            reverse("engagements:case-list")
            + "?status=open&priority=high&search=MyTenantTitle"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case["tenant"], self.tenant.id)
            self.assertIn("MyTenantTitle", case["title"])


