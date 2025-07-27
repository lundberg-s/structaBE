from django.urls import reverse
from rest_framework import status
from relations.tests.client.test_base import FullySetupTest
from relations.tests.factory import (
    create_person, create_organization, create_role, create_relation
)
from relations.models import Relation
from relations.choices import RelationObjectType

class TestRelationViews(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.person = create_person(self.tenant)
        self.org = create_organization(self.tenant)
        self.member_role = create_role(self.tenant, label="Member", is_system=False)
        self.customer_role = create_role(self.tenant, label="Customer", is_system=False)

    def test_create_relation_person_to_org(self):
        self.authenticate_client()
        data = {
            'source_partner_id': str(self.person.id),
            'target_partner_id': str(self.org.id),
            'role_id': str(self.member_role.id)
        }
        url = reverse('relations:relation-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        relation = Relation.objects.get(id=response.data['id'])
        self.assertEqual(relation.source_partner, self.person)
        self.assertEqual(relation.target_partner, self.org)
        self.assertEqual(relation.role, self.member_role)
        self.assertEqual(relation.tenant, self.tenant)

    def test_create_relation_org_to_person(self):
        self.authenticate_client()
        data = {
            'source_partner_id': str(self.org.id),
            'target_partner_id': str(self.person.id),
            'role_id': str(self.customer_role.id)
        }
        url = reverse('relations:relation-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        relation = Relation.objects.get(id=response.data['id'])
        self.assertEqual(relation.source_partner, self.org)
        self.assertEqual(relation.target_partner, self.person)
        self.assertEqual(relation.role, self.customer_role)
        self.assertEqual(relation.tenant, self.tenant)

    def test_relation_same_source_target_invalid(self):
        self.authenticate_client()
        data = {
            'source_partner_id': str(self.person.id),
            'target_partner_id': str(self.person.id),
            'role_id': str(self.member_role.id)
        }
        url = reverse('relations:relation-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relation_tenant_isolation(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_person = create_person(other_tenant)
        other_role = create_role(other_tenant, label="Member", is_system=False)
        
        # Create relation in other tenant
        relation = create_relation(other_tenant, other_person, self.org, other_role)
        
        # Try to access other tenant's relation
        url = reverse('relations:relation-detail', args=[relation.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_list_relations(self):
        self.authenticate_client()
        # Create a relation first
        create_relation(self.tenant, self.person, self.org, self.member_role)
        
        url = reverse('relations:relation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_retrieve_relation(self):
        self.authenticate_client()
        relation = create_relation(self.tenant, self.person, self.org, self.member_role)
        
        url = reverse('relations:relation-detail', args=[relation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(relation.id)) 