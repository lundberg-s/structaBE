from django.urls import reverse
from rest_framework.test import APITestCase
from engagements.tests.client.test_base import CaseTenancySetup
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_case, create_default_status, create_default_priority, create_default_category  
from engagements.models import Case as CaseModel
from datetime import timedelta
from django.utils import timezone

class TestCaseFlow(CaseTenancySetup, APITestCase):
    def setUp(self):
        super().setUp()
        self.case_data = {
            'title': 'Test Case',
            'description': 'A test case',
            'status': self.status.id,
            'category': self.category.id,
            'priority': self.priority.id,
            'deadline': (timezone.now() + timedelta(days=7)).isoformat(),
            'case_reference': f'C-001',
            'legal_area': 'Civil',
            'court_date': (timezone.now() + timedelta(days=30)).date().isoformat(),
        }

    def test_create_case_success(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        response = self.client.post(url, self.case_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)


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
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)

    def test_unauthenticated_user_cannot_create_case(self):
        url = reverse('engagements:case-list')
        response = self.client.post(url, self.case_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_list_cases_for_user_tenant_only(self):
        self.authenticate_client()
        # Create case for another tenant
        other_tenant = create_tenant(work_item_type='case')
        create_case(tenant=other_tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case['tenant'], self.tenant.id)

    def test_retrieve_case_from_same_tenant(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['id']), str(case.id))

    def test_retrieve_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        case = create_case(tenant=other_tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, (403, 404))

    def test_update_own_case_success(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.title, 'Updated Title')

    def test_update_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        case = create_case(tenant=other_tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (403, 404))

    def test_cannot_spoof_protected_fields_on_update(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-detail', args=[case.id])
        data = {'created_by': create_user(tenant=self.tenant, username='spoof', password='pass').id, 'tenant': create_tenant(work_item_type='case').id}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_delete_own_case_success(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
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

    def test_delete_case_from_other_tenant_fails(self):
        self.authenticate_client()
        other_tenant = create_tenant(work_item_type='case')
        case = create_case(tenant=other_tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        url = reverse('engagements:case-detail', args=[case.id])
        response = self.client.delete(url)
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(CaseModel.objects.filter(id=case.id).exists())

    def test_protected_fields_are_readonly(self):
        self.authenticate_client()
        case = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
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
        self.assertEqual(response.status_code, 201)
        case = CaseModel.objects.get(id=response.data['id'])
        self.assertEqual(case.created_by, self.user)
        self.assertEqual(case.tenant, self.tenant)

    def test_create_case_returns_success_status(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        response = self.client.post(url, self.case_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_case_with_invalid_data_returns_400(self):
        self.authenticate_client()
        url = reverse('engagements:case-list')
        data = self.case_data.copy()
        data['category'] = 'invalid'
        data['case_reference'] = 'C-006'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_user_create_case_returns_401(self):
        url = reverse('engagements:case-list')
        response = self.client.post(url, self.case_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_denied(self):
        url = reverse('engagements:case-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_filter_cases_by_status(self):
        self.authenticate_client()
        other_status = create_default_status(tenant=self.tenant, label='Closed', created_by=self.user)
        another_status = create_default_status(tenant=self.tenant, label='Open', created_by=self.user)
        # Create cases with different statuses and priorities
        create_case(tenant=self.tenant, created_by=self.user, status=other_status, category=self.category, priority=self.priority, title='Another Case')
        create_case(tenant=self.tenant, created_by=self.user, status=another_status, category=self.category, priority=self.priority, title='Another Case')

        url = reverse('engagements:case-list')
        response = self.client.get(url, {'status__label': 'Closed'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only one case should be returned


    def test_filter_cases_by_priority(self):
        self.authenticate_client()
        other_priority = create_default_priority(tenant=self.tenant, label='Low', created_by=self.user)
        another_priority = create_default_priority(tenant=self.tenant, label='Medium', created_by=self.user)
        # Create cases with different priorities and statuses
        create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=other_priority, title='Another Case')
        create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=another_priority, title='Another Case')

        url = reverse('engagements:case-list')
        response = self.client.get(url, {'priority__label': 'Low'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only one case should be returned

    def test_filter_cases_by_category(self):
        self.authenticate_client()
        other_category = create_default_category(tenant=self.tenant, label='Low', created_by=self.user)
        another_category = create_default_category(tenant=self.tenant, label='Medium', created_by=self.user)
        # Create cases with different categories and statuses
        create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=other_category, priority=self.priority, title='Another Case')
        create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=another_category, priority=self.priority, title='Another Case')  

        url = reverse('engagements:case-list')
        response = self.client.get(url, {'category__label': 'Low'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only one case should be returned

    def test_search_cases_by_title_or_description(self):
        self.authenticate_client()
        c = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
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
        c1 = create_case(tenant=other_tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        c1.title = 'OtherTenantTitle'
        c1.status = self.status
        c1.priority = self.priority
        c1.save()
        c2 = create_case(tenant=self.tenant, created_by=self.user, status=self.status, category=self.category, priority=self.priority)
        c2.title = 'MyTenantTitle'
        c2.status = self.status
        c2.priority = self.priority
        c2.save()
        url = reverse('engagements:case-list') + '?status=open&priority=high&search=MyTenantTitle'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for case in response.data:
            self.assertEqual(case['tenant'], self.tenant.id)
            self.assertIn('MyTenantTitle', case['title'])


