from django.urls import reverse
from rest_framework import status
from relations.tests.client.test_base import FullySetupTest
from relations.tests.factory import (
    create_person, create_organization, create_relation_reference_for_person, 
    create_relation_reference_for_organization, create_role, create_relation
)
from relations.models import Relation, Role, RelationReference
from relations.choices import RelationObjectType, SystemRole
from engagements.models import Ticket
from engagements.models import WorkItemStatusTypes, WorkItemPriorityTypes, WorkItemCategoryTypes
from users.tests.factory import create_user


class TestWorkItemIntegration(FullySetupTest):
    """
    Test the full SAP-style CRM workflow using our Relation system:
    1. Create a ticket (work item)
    2. Create a person (partner)
    3. Create a relation between the ticket and person
    4. Assign a role to the person in relation to the ticket
    5. Verify the relationships work correctly
    """
    
    def setUp(self):
        super().setUp()
        # Create test data
        self.person = create_person(self.tenant, first_name="John", last_name="Customer")
        self.org = create_organization(self.tenant, name="Customer Corp")
        
        # Create relation references
        self.person_ref = create_relation_reference_for_person(self.person)
        self.org_ref = create_relation_reference_for_organization(self.org)
        
        # Create a ticket
        self.ticket = Ticket.objects.create(
            tenant=self.tenant,
            title="Customer Support Request",
            description="Need help with our account",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.TICKET,
            priority=WorkItemPriorityTypes.MEDIUM,
            created_by=self.user,
            ticket_number="TICK-001"
        )
        
        # Create relation reference for the ticket
        self.ticket_ref = RelationReference.objects.create(
            type=RelationObjectType.WORKITEM,
            workitem=self.ticket
        )

    def test_create_ticket_person_relationship(self):
        """Test creating a relationship between a ticket and a person"""
        self.authenticate_client()
        
        # Create relation: Person -> Ticket (customer relationship)
        data = {
            'source_id': str(self.person_ref.id),
            'target_id': str(self.ticket_ref.id),
            'relation_type': 'customer_of'
        }
        
        url = reverse('relations:relation-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the relation was created correctly
        relation = Relation.objects.get(id=response.data['id'])
        self.assertEqual(relation.source, self.person_ref)
        self.assertEqual(relation.target, self.ticket_ref)
        self.assertEqual(relation.relation_type, 'customer_of')
        self.assertEqual(relation.tenant, self.tenant)

    def test_assign_customer_role_to_person_for_ticket(self):
        """Test assigning a customer role to a person for a specific ticket"""
        self.authenticate_client()
        
        # Create relation first
        relation = create_relation(
            self.tenant, 
            self.person_ref, 
            self.ticket_ref, 
            relation_type='customer_of'
        )
        
        # Assign customer role to the person for this ticket
        data = {
            'target': str(self.person_ref.id),
            'system_role': SystemRole.CUSTOMER,
            'custom_role': None
        }
        
        url = reverse('relations:role-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the role was assigned correctly
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(role.target, self.person_ref)
        self.assertEqual(role.system_role, SystemRole.CUSTOMER)
        self.assertEqual(role.tenant, self.tenant)

    def test_assign_custom_role_to_person_for_ticket(self):
        """Test assigning a custom role to a person for a specific ticket"""
        self.authenticate_client()
        
        # Create a custom role
        from relations.tests.factory import create_custom_role
        custom_role = create_custom_role(self.tenant, key='premium_customer', label='Premium Customer')
        
        # Create relation first
        relation = create_relation(
            self.tenant, 
            self.person_ref, 
            self.ticket_ref, 
            relation_type='customer_of'
        )
        
        # Assign custom role to the person for this ticket
        data = {
            'target': str(self.person_ref.id),
            'system_role': None,
            'custom_role': custom_role.id
        }
        
        url = reverse('relations:role-list')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the role was assigned correctly
        role = Role.objects.get(id=response.data['id'])
        self.assertEqual(role.target, self.person_ref)
        self.assertEqual(role.custom_role, custom_role)
        self.assertEqual(role.tenant, self.tenant)

    def test_complex_workflow_ticket_with_multiple_partners(self):
        """Test a complex workflow with a ticket, customer, and vendor"""
        self.authenticate_client()
        
        # Create additional partners
        vendor_person = create_person(self.tenant, first_name="Vendor", last_name="Support")
        vendor_ref = create_relation_reference_for_person(vendor_person)
        
        # Create relations
        customer_relation = create_relation(
            self.tenant, 
            self.person_ref, 
            self.ticket_ref, 
            relation_type='customer_of'
        )
        
        vendor_relation = create_relation(
            self.tenant, 
            vendor_ref, 
            self.ticket_ref, 
            relation_type='vendor_for'
        )
        
        # Assign roles
        customer_role = create_role(
            self.tenant, 
            self.person_ref, 
            system_role=SystemRole.CUSTOMER
        )
        
        vendor_role = create_role(
            self.tenant, 
            vendor_ref, 
            system_role=SystemRole.VENDOR
        )
        
        # Verify the complete setup
        self.assertEqual(Relation.objects.count(), 2)
        self.assertEqual(Role.objects.count(), 2)
        
        # Verify customer relationship
        customer_relation = Relation.objects.get(source=self.person_ref, target=self.ticket_ref)
        self.assertEqual(customer_relation.relation_type, 'customer_of')
        
        # Verify vendor relationship
        vendor_relation = Relation.objects.get(source=vendor_ref, target=self.ticket_ref)
        self.assertEqual(vendor_relation.relation_type, 'vendor_for')
        
        # Verify roles
        customer_role = Role.objects.get(target=self.person_ref, system_role=SystemRole.CUSTOMER)
        vendor_role = Role.objects.get(target=vendor_ref, system_role=SystemRole.VENDOR)

    def test_work_item_relation_integration(self):
        """Test integration using our Relation system for work items"""
        # Create a relation using our new system
        relation = create_relation(
            self.tenant, 
            self.person_ref, 
            self.ticket_ref, 
            relation_type='customer_of'
        )
        
        # Assign a role
        role = create_role(
            self.tenant, 
            self.person_ref, 
            system_role=SystemRole.CUSTOMER
        )
        
        # Verify the relation was created
        self.assertEqual(Relation.objects.count(), 1)
        self.assertEqual(Role.objects.count(), 1)
        
        # Verify the relation details
        relation = Relation.objects.get(source=self.person_ref, target=self.ticket_ref)
        self.assertEqual(relation.relation_type, 'customer_of')
        self.assertEqual(relation.tenant, self.tenant)

    def test_tenant_isolation_for_work_item_relations(self):
        """Test that work item relations are properly isolated by tenant"""
        self.authenticate_client()
        
        # Create another tenant and its data
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_user = create_user(other_tenant, username='otheruser', email='otheruser@example.com')
        other_person = create_person(other_tenant)
        other_person_ref = create_relation_reference_for_person(other_person)
        
        other_ticket = Ticket.objects.create(
            tenant=other_tenant,
            title="Other Ticket",
            description="Other tenant's ticket",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.TICKET,
            priority=WorkItemPriorityTypes.MEDIUM,
            created_by=other_user,
            ticket_number="TICK-002"
        )
        
        other_ticket_ref = RelationReference.objects.create(
            type=RelationObjectType.WORKITEM,
            workitem=other_ticket
        )
        
        # Create relation in other tenant
        other_relation = create_relation(
            other_tenant, 
            other_person_ref, 
            other_ticket_ref, 
            relation_type='customer_of'
        )
        
        # Try to access other tenant's relation from current tenant
        url = reverse('relations:relation-detail', args=[other_relation.id])
        response = self.client.get(url)
        
        # Should be denied access
        self.assertIn(response.status_code, (403, 404))

    def test_full_crm_workflow(self):
        """Test the complete CRM workflow: ticket -> person -> relation -> role"""
        self.authenticate_client()
        
        # Step 1: Create a ticket
        ticket = Ticket.objects.create(
            tenant=self.tenant,
            title="Technical Support Issue",
            description="Cannot access the system",
            status=WorkItemStatusTypes.OPEN,
            category=WorkItemCategoryTypes.TICKET,
            priority=WorkItemPriorityTypes.HIGH,
            created_by=self.user,
            ticket_number="TICK-003"
        )
        
        # Step 2: Create relation reference for the ticket
        ticket_ref = RelationReference.objects.create(
            type=RelationObjectType.WORKITEM,
            workitem=ticket
        )
        
        # Step 3: Create a customer person
        customer = create_person(self.tenant, first_name="Alice", last_name="Customer")
        customer_ref = create_relation_reference_for_person(customer)
        
        # Step 4: Create relation between customer and ticket
        relation_data = {
            'source_id': str(customer_ref.id),
            'target_id': str(ticket_ref.id),
            'relation_type': 'customer_of'
        }
        
        url = reverse('relations:relation-list')
        response = self.client.post(url, relation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 5: Assign customer role
        role_data = {
            'target': str(customer_ref.id),
            'system_role': SystemRole.CUSTOMER,
            'custom_role': None
        }
        
        url = reverse('relations:role-list')
        response = self.client.post(url, role_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 6: Verify the complete setup
        relation = Relation.objects.get(source=customer_ref, target=ticket_ref)
        role = Role.objects.get(target=customer_ref, system_role=SystemRole.CUSTOMER)
        
        self.assertEqual(relation.relation_type, 'customer_of')
        self.assertEqual(role.system_role, SystemRole.CUSTOMER)
        self.assertEqual(relation.tenant, self.tenant)
        self.assertEqual(role.tenant, self.tenant) 