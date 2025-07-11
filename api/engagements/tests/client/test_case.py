from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_case
from engagements.tests.client.test_base import Case
from engagements.models import Case as CaseModel
from datetime import timedelta
from django.utils import timezone

class TestCaseFlow(Case, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.case_data = {
            'title': 'Test Case',
            'description': 'A test case',
            'status': 'open',
            'category': 'case',
            'priority': 'medium',
            'deadline': (timezone.now() + timedelta(days=7)).isoformat(),
            'case_reference': f'C-001',
            'legal_area': 'Civil',
            'court_date': (timezone.now() + timedelta(days=30)).date().isoformat(),
        }

    def test_create_case_success(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        response = self.client.post(url, self.case_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        case = CaseModel.objects.get(id=response.data['id'])
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_create_case_auto_sets_user_and_tenant(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        other_tenant = create_tenant(work_item_type='case')
        url = reverse('engagements:case-list')
        data = self.case_data.copy()
        data['created_by'] = other_user.id
        data['tenant'] = other_tenant.id
        data['case_reference'] = 'C-002'
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        case = CaseModel.objects.get(id=response.data['id'])
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_create_case_invalid_foreign_key(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        # Invalid category
        data = self.case_data.copy()
        data['category'] = 'invalid'
        data['case_reference'] = 'C-003'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid status
        data = self.case_data.copy()
        data['status'] = 'invalid'
        data['case_reference'] = 'C-004'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_cannot_create_case(self):
        url = reverse('engagements:case-list')
        response = self.client.post(url, self.case_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_list_cases_for_user_tenant_only(self):
        self.authenticate_client()
        # Create case for another tenant
        other_tenant = create_tenant(work_item_type='case')
        create_case(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:case-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case['tenant'], self.tenant.id)

    def test_retrieve_case_from_same_tenant(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['id']), str(case.id))

    def test_retrieve_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        case = create_case(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_case_success(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.title, 'Updated Title')

    def test_update_case_from_other_user_fails(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        case = create_case(tenant=self.tenant, created_by=other_user)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_update_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        case = create_case(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_cannot_spoof_protected_fields_on_update(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'created_by': create_user(tenant=self.tenant, username='spoof', password='pass').id, 'tenant': create_tenant(work_item_type='case').id}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_delete_own_case_success(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        case.refresh_from_db()
        self.assertTrue(case.is_deleted)
        # Optionally check not in list or detail
        list_url = reverse('engagements:case-list')
        list_response = self.client.get(list_url)
        self.assertFalse(any(c['id'] == str(case.id) for c in list_response.data))
        detail_response = self.client.get(url)
        self.assertEqual(detail_response.status_code, 404)

    def test_delete_case_from_other_user_fails(self):
        self.authenticate_client()
        other_user = create_user(tenant=self.tenant, username='otheruser', password='otherpass')
        case = create_case(tenant=self.tenant, created_by=other_user)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(CaseModel.objects.filter(id=case.id).exists())

    def test_delete_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        case = create_case(tenant=other_tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(CaseModel.objects.filter(id=case.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'created_at': '2000-01-01T00:00:00Z'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertNotEqual(str(case.created_at), '2000-01-01T00:00:00Z')

    def test_cannot_spoof_protected_fields_on_create(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        data = self.case_data.copy()
        data['created_by'] = create_user(tenant=self.tenant, username='spoof', password='pass').id
        data['tenant'] = create_tenant(work_item_type='case').id
        data['case_reference'] = 'C-005'
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, (200, 201))
        case = CaseModel.objects.get(id=response.data['id'])
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_http_status_codes_are_correct(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        # Valid create
        response = self.client.post(url, self.case_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        # Invalid create
        data = self.case_data.copy()
        data['category'] = 'invalid'
        data['case_reference'] = 'C-006'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Unauthenticated
        self.client.logout()
        response = self.client.post(url, self.case_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_denied(self):
        url = reverse('engagements:case-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_cases_by_status_and_priority(self):
        self.authenticate_client()
        c1 = create_case(tenant=self.tenant, created_by=self.user)
        c1.status = 'open'
        c1.priority = 'high'
        c1.save()
        c2 = create_case(tenant=self.tenant, created_by=self.user)
        c2.status = 'closed'
        c2.priority = 'low'
        c2.save()
        url = reverse('engagements:case-list') + '?status=open&priority=high'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case['status'], 'open')
            self.assertEqual(case['priority'], 'high')

    def test_search_cases_by_title_or_description(self):
        self.authenticate_client()
        c = create_case(tenant=self.tenant, created_by=self.user)
        c.title = 'UniqueTitle'
        c.description = 'SpecialDesc'
        c.save()
        url = reverse('engagements:case-list') + '?search=UniqueTitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('UniqueTitle' in c['title'] for c in response.data))

    def test_filter_and_search_results_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        c1 = create_case(tenant=other_tenant, created_by=self.user)
        c1.title = 'OtherTenantTitle'
        c1.status = 'open'
        c1.priority = 'high'
        c1.save()
        c2 = create_case(tenant=self.tenant, created_by=self.user)
        c2.title = 'MyTenantTitle'
        c2.status = 'open'
        c2.priority = 'high'
        c2.save()
        url = reverse('engagements:case-list') + '?status=open&priority=high&search=MyTenantTitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case['tenant'], self.tenant.id)
            self.assertIn('MyTenantTitle', case['title'])

    def test_case_partner_roles_are_serialized(self):
        self.authenticate_client()
        from engagements.tests.factory import create_case
        case = create_case(tenant=self.tenant, created_by=self.user)
        from relations.models import Organization
        from django.contrib.contenttypes.models import ContentType
        org = Organization.objects.create(tenant=self.tenant, name='Test Org')
        content_type = ContentType.objects.get_for_model(Organization)
        from engagements.models import WorkItemPartnerRole
        WorkItemPartnerRole.objects.create(
            tenant=self.tenant,
            work_item=case,
            content_type=content_type,
            object_id=org.id,
            role='customer',
        )
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('partner_roles', response.data)
        self.assertGreater(len(response.data['partner_roles']), 0)
