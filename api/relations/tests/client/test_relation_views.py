from django.urls import reverse
from rest_framework import status
from relations.tests.client.test_base import FullySetupTest
from relations.tests.factory import (
    create_person, create_organization, create_relation_reference_for_person, create_relation_reference_for_organization,
    create_relation
)
from relations.models import Relation

class TestRelationViews(FullySetupTest):
    def setUp(self):
        super().setUp()
        self.person = create_person(self.tenant)
        self.org = create_organization(self.tenant)
        self.person_ref = create_relation_reference_for_person(self.person)
        self.org_ref = create_relation_reference_for_organization(self.org)

    def test_create_relation(self):
        self.authenticate_client()
        data = {
            'source_id': str(self.person_ref.id),
            'target_id': str(self.org_ref.id),
            'relation_type': 'member_of'
        }
        url = reverse('relations:relation-list')
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        relation = Relation.objects.get(id=response.data['id'])
        self.assertEqual(relation.source, self.person_ref)
        self.assertEqual(relation.target, self.org_ref)
        self.assertEqual(relation.tenant, self.tenant)
        self.assertEqual(relation.relation_type, 'member_of')

    def test_relation_same_source_target_invalid(self):
        self.authenticate_client()
        data = {
            'source_id': str(self.person_ref.id),
            'target_id': str(self.person_ref.id),
            'relation_type': 'self'
        }
        url = reverse('relations:relation-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_relation_tenant_isolation(self):
        self.authenticate_client()
        from core.tests.factory import create_tenant
        other_tenant = create_tenant()
        other_person = create_person(other_tenant)
        other_person_ref = create_relation_reference_for_person(other_person)
        relation = create_relation(other_tenant, other_person_ref, self.org_ref, relation_type='member_of')
        url = reverse('relations:relation-detail', args=[relation.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404)) 