from django.urls import reverse
from rest_framework.test import APITestCase

from engagements.tests.client.test_base import TicketTenancySetup
from engagements.tests.factory import (
    create_ticket,
    create_default_status,
    create_default_priority,
    create_default_category,
)
from core.tests.factory import create_tenant
from users.tests.factory import create_user
from engagements.models import Ticket


class TestTicketFlow(TicketTenancySetup, APITestCase):
    def setUp(self):
        super().setUp()
        self.ticket_data = {
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "status": self.status.id,
            "category": self.category.id,
            "priority": self.priority.id,
        }

    def test_create_ticket_success(self):
        self.authenticate_client()
        url = reverse("engagements:ticket-list")
        response = self.client.post(url, self.ticket_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)

    def test_create_ticket_auto_sets_user_and_tenant(self):
        self.authenticate_client()
        url = reverse("engagements:ticket-list")
        response = self.client.post(url, self.ticket_data, format="json")
        self.assertEqual(response.status_code, 201)
        ticket = Ticket.objects.get(id=response.data["id"])
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_create_ticket_invalid_foreign_key(self):
        self.authenticate_client()
        url = reverse("engagements:ticket-list")
        data = self.ticket_data.copy()
        data["status"] = "invalid_status"  # Invalid status value
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_ticket(self):
        url = reverse("engagements:ticket-list")
        response = self.client.post(url, self.ticket_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_list_tickets_for_user_tenant_only(self):
        self.authenticate_client()
        # Create ticket for current tenant
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        # Create ticket for other tenant
        other_tenant = create_tenant()
        create_ticket(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )

        url = reverse("engagements:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data), 2
        )  # Should only see tickets from current tenant

    def test_retrieve_ticket_from_same_tenant(self):
        self.authenticate_client()
        ticket = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["id"]), str(ticket.id))

    def test_retrieve_ticket_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        ticket = create_ticket(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_ticket_success(self):
        self.authenticate_client()
        ticket = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.title, "Updated Title")

    def test_update_ticket_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        ticket = create_ticket(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        data = {"title": "Hacked"}
        response = self.client.patch(url, data, format="json")
        self.assertIn(response.status_code, (403, 404))

    def test_cannot_spoof_protected_fields_on_update(self):
        self.authenticate_client()
        ticket = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        data = {
            "created_by": create_user(
                tenant=self.tenant, username="spoof", password="pass"
            ).id,
            "tenant": create_tenant().id,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_delete_own_ticket_success(self):
        self.authenticate_client()
        ticket = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_deleted)
        # Optionally check not in list or detail
        list_url = reverse("engagements:ticket-list")
        list_response = self.client.get(list_url)
        self.assertFalse(any(t["id"] == str(ticket.id) for t in list_response.data))
        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        ticket = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
        )
        url = reverse("engagements:ticket-detail", args=[ticket.id])
        data = {"created_at": "2000-01-01T00:00:00Z"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertNotEqual(str(ticket.created_at), "2000-01-01T00:00:00Z")

    def test_cannot_spoof_protected_fields_on_create(self):
        self.authenticate_client()
        url = reverse("engagements:ticket-list")
        data = self.ticket_data.copy()
        data["created_by"] = create_user(
            tenant=self.tenant, username="spoof", password="pass"
        ).id
        data["tenant"] = create_tenant().id
        response = self.client.post(url, data, format="json")
        self.assertIn(response.status_code, (200, 201))
        ticket = Ticket.objects.get(id=response.data["id"])
        self.assertEqual(ticket.created_by, self.user)
        self.assertEqual(ticket.tenant, self.tenant)

    def test_http_status_codes_are_correct(self):
        self.authenticate_client()
        url = reverse("engagements:ticket-list")
        # Valid create
        response = self.client.post(url, self.ticket_data, format="json")
        self.assertIn(response.status_code, (200, 201))
        # Invalid create
        data = self.ticket_data.copy()
        data["category"] = "invalid"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        # Unauthenticated
        self.client.logout()
        response = self.client.post(url, self.ticket_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_denied(self):
        url = reverse("engagements:ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_tickets_by_status(self):
        self.authenticate_client()
        other_status = create_default_status(
            tenant=self.tenant, label="Closed", created_by=self.user
        )
        another_status = create_default_status(
            tenant=self.tenant, label="Open", created_by=self.user
        )
        # Create tickets with different statuses and priorities
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=other_status,
            category=self.category,
            priority=self.priority,
            title="Another Ticket",
        )
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=another_status,
            category=self.category,
            priority=self.priority,
            title="Another Ticket",
        )

        url = reverse("engagements:ticket-list")
        response = self.client.get(url, {"status__label": "Closed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only one ticket should be returned

    def test_filter_tickets_by_priority(self):
        self.authenticate_client()
        other_priority = create_default_priority(
            tenant=self.tenant, label="Low", created_by=self.user
        )
        another_priority = create_default_priority(
            tenant=self.tenant, label="Medium", created_by=self.user
        )
        # Create tickets with different priorities and statuses
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=other_priority,
            title="Another Ticket",
        )
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=another_priority,
            title="Another Ticket",
        )

        url = reverse("engagements:ticket-list")
        response = self.client.get(url, {"priority__label": "Low"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only one ticket should be returned

    def test_filter_tickets_by_category(self):
        self.authenticate_client()
        other_category = create_default_category(
            tenant=self.tenant, label="Low", created_by=self.user
        )
        another_category = create_default_category(
            tenant=self.tenant, label="Medium", created_by=self.user
        )
        # Create tickets with different categories and statuses
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=other_category,
            priority=self.priority,
            title="Another Ticket",
        )
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=another_category,
            priority=self.priority,
            title="Another Ticket",
        )

        url = reverse("engagements:ticket-list")
        response = self.client.get(url, {"category__label": "Low"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only one ticket should be returned

    def test_search_tickets_by_title_or_description(self):
        self.authenticate_client()
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
            title="Special Ticket",
            description="Important issue",
        )
        create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
            title="Regular Ticket",
            description="Normal issue",
        )

        url = reverse("engagements:ticket-list")
        response = self.client.get(url, {"search": "Special"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("Special", response.data[0]["title"])

    def test_filter_and_search_results_scoped_to_tenant(self):
        self.authenticate_client()
        # Create tickets in current tenant
        t1 = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
            title="Tenant A Ticket",
        )
        t2 = create_ticket(
            tenant=self.tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
            title="Tenant A Another",
        )

        # Create ticket in other tenant
        other_tenant = create_tenant()
        t3 = create_ticket(
            tenant=other_tenant,
            created_by=self.user,
            status=self.status,
            category=self.category,
            priority=self.priority,
            title="Tenant B Ticket",
        )

        url = reverse("engagements:ticket-list")
        response = self.client.get(url, {"search": "Ticket"})
        self.assertEqual(response.status_code, 200)

        # Should only see tickets from current tenant
        ticket_ids = [t["id"] for t in response.data]
        self.assertIn(str(t1.id), ticket_ids)
        self.assertIn(str(t2.id), ticket_ids)
        self.assertNotIn(str(t3.id), ticket_ids)
