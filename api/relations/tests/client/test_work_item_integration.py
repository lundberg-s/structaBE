from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from relations.tests.factory import create_person, create_organization, create_role
from relations.models import Relation
from engagements.models import Ticket
from engagements.choices.work_item_choices import (
    WorkItemStatusTypes,
    WorkItemCategoryTypes,
    WorkItemPriorityTypes,
)
from relations.tests.factory import create_tenant, create_user


class TestWorkItemIntegration(TestCase):
    """Test integration between work items and relations"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create tenant and user
        self.tenant = create_tenant()
        self.user = create_user(tenant=self.tenant)

        # Create partners
        self.person = create_person(self.tenant, first_name="John", last_name="Doe")
        self.org = create_organization(self.tenant, name="Acme Corp")

        # Create a ticket
        self.ticket = Ticket.objects.create(
            tenant=self.tenant,
            title="Customer Support Request",
            description="Need help with our account",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.SUPPORT,
            priority=WorkItemPriorityTypes.MEDIUM,
            created_by=self.user,
            ticket_number="TICK-001",
        )

    def test_create_ticket_person_relationship(self):
        """Test creating a relationship between a ticket and a person"""
        self.client.force_authenticate(user=self.user)

        # Create a role for the relationship
        role = create_role(
            self.tenant, key="customer", label="Customer", is_system=False
        )

        # Create relation: Ticket -> Person (customer relationship)
        data = {
            "source_workitem_id": str(self.ticket.id),
            "target_partner_id": str(self.person.id),
            "role_id": str(role.id),
        }

        url = reverse("relations:relation-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the relation was created correctly
        relation = Relation.objects.get(id=response.data["id"])
        self.assertEqual(relation.source_workitem.id, self.ticket.id)
        self.assertEqual(relation.target_partner.id, self.person.id)
        self.assertEqual(relation.role, role)
        self.assertEqual(relation.tenant, self.tenant)

    def test_create_person_ticket_relationship(self):
        """Test creating a relationship between a person and a ticket"""
        self.client.force_authenticate(user=self.user)

        # Create a role for the relationship
        role = create_role(
            self.tenant, key="customer", label="Customer", is_system=False
        )

        # Create relation: Person -> Ticket (customer relationship)
        data = {
            "source_partner_id": str(self.person.id),
            "target_workitem_id": str(self.ticket.id),
            "role_id": str(role.id),
        }

        url = reverse("relations:relation-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the relation was created correctly
        relation = Relation.objects.get(id=response.data["id"])
        self.assertEqual(relation.source_partner.id, self.person.id)
        self.assertEqual(relation.target_workitem.id, self.ticket.id)
        self.assertEqual(relation.role, role)
        self.assertEqual(relation.tenant, self.tenant)

    def test_create_organization_ticket_relationship(self):
        """Test creating a relationship between an organization and a ticket"""
        self.client.force_authenticate(user=self.user)

        # Create a role for the relationship
        role = create_role(self.tenant, key="vendor", label="Vendor", is_system=False)

        # Create relation: Organization -> Ticket (vendor relationship)
        data = {
            "source_partner_id": str(self.org.id),
            "target_workitem_id": str(self.ticket.id),
            "role_id": str(role.id),
        }

        url = reverse("relations:relation-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the relation was created correctly
        relation = Relation.objects.get(id=response.data["id"])
        self.assertEqual(relation.source_partner.id, self.org.id)
        self.assertEqual(relation.target_workitem.id, self.ticket.id)
        self.assertEqual(relation.role, role)
        self.assertEqual(relation.tenant, self.tenant)

    def test_tenant_isolation_for_work_item_relations(self):
        """Test that relations are properly isolated by tenant"""
        # Create another tenant and user
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant)

        # Create partners in other tenant
        other_person = create_person(other_tenant, first_name="Jane", last_name="Smith")
        other_ticket = Ticket.objects.create(
            tenant=other_tenant,
            title="Other Ticket",
            description="Other ticket description",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.SUPPORT,
            priority=WorkItemPriorityTypes.MEDIUM,
            created_by=other_user,
            ticket_number="TICK-002",
        )

        # Create role in other tenant
        other_role = create_role(other_tenant, label="Customer", is_system=False)

        # Authenticate as other user
        self.client.force_authenticate(user=other_user)

        # Create relation in other tenant
        data = {
            "source_partner_id": str(other_person.id),
            "target_workitem_id": str(other_ticket.id),
            "role_id": str(other_role.id),
        }

        url = reverse("relations:relation-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the relation was created in the correct tenant
        relation = Relation.objects.get(id=response.data["id"])
        self.assertEqual(relation.tenant, other_tenant)

        # Verify that relations from different tenants are isolated
        all_relations = Relation.objects.all()
        self.assertEqual(all_relations.count(), 1)
        self.assertEqual(all_relations.first().tenant, other_tenant)

    def test_full_crm_workflow(self):
        """Test a complete CRM workflow with multiple relationships"""
        self.client.force_authenticate(user=self.user)

        # Create multiple roles
        customer_role = create_role(self.tenant, label="Customer", is_system=False)
        vendor_role = create_role(self.tenant, label="Vendor", is_system=False)
        employee_role = create_role(self.tenant, label="Employee", is_system=False)

        # Create additional partners
        vendor = create_organization(self.tenant, name="Tech Solutions Inc")
        employee = create_person(self.tenant, first_name="Alice", last_name="Johnson")

        # Create multiple tickets
        support_ticket = Ticket.objects.create(
            tenant=self.tenant,
            title="Technical Support",
            description="Need technical assistance",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.SUPPORT,
            priority=WorkItemPriorityTypes.HIGH,
            created_by=self.user,
            ticket_number="TICK-003",
        )

        purchase_ticket = Ticket.objects.create(
            tenant=self.tenant,
            title="Purchase Order",
            description="New equipment purchase",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.TASK,
            priority=WorkItemPriorityTypes.MEDIUM,
            created_by=self.user,
            ticket_number="TICK-004",
        )

        # Create multiple relationships
        relations_data = [
            # Customer relationship
            {
                "source_partner_id": str(self.person.id),
                "target_workitem_id": str(support_ticket.id),
                "role_id": str(customer_role.id),
            },
            # Vendor relationship
            {
                "source_partner_id": str(vendor.id),
                "target_workitem_id": str(purchase_ticket.id),
                "role_id": str(vendor_role.id),
            },
            # Employee relationship
            {
                "source_partner_id": str(employee.id),
                "target_workitem_id": str(support_ticket.id),
                "role_id": str(employee_role.id),
            },
        ]

        url = reverse("relations:relation-list")
        created_relations = []

        for data in relations_data:
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_relations.append(response.data["id"])

        # Verify all relations were created
        self.assertEqual(len(created_relations), 3)

        # Verify the relationships are correct
        relations = Relation.objects.filter(id__in=created_relations)
        self.assertEqual(relations.count(), 3)

        # Check specific relationships
        customer_relation = relations.filter(
            source_partner=self.person,
            target_workitem=support_ticket,
            role=customer_role,
        ).first()
        self.assertIsNotNone(customer_relation)

        vendor_relation = relations.filter(
            source_partner=vendor, target_workitem=purchase_ticket, role=vendor_role
        ).first()
        self.assertIsNotNone(vendor_relation)

        employee_relation = relations.filter(
            source_partner=employee, target_workitem=support_ticket, role=employee_role
        ).first()
        self.assertIsNotNone(employee_relation)
