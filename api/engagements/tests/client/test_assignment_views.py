from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.tests.factory import create_user
from core.tests.factory import create_tenant
from engagements.tests.factory import create_ticket, create_assignment
from engagements.tests.client.test_base import FullySetupTest
from engagements.models import Assignment

class TestAssignmentFlow(FullySetupTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.work_item = self.ticket
        self.assignee = create_user(tenant=self.tenant, username='assignee', email='assignee@example.com')
        self.assignment_data = {
            'work_item': str(self.work_item.id),
            'user': self.assignee.id,
        }

    def test_create_assignment_success(self):
        self.authenticate_client()
        url = reverse('engagements:assignment-create')
        response = self.client.post(url, self.assignment_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        assignment = Assignment.objects.get(id=response.data['id'])
        self.assertEqual(assignment.user.id, self.assignee.id)
        self.assertEqual(assignment.work_item.id, self.work_item.id)
        self.assertEqual(assignment.assigned_by, self.user)

    def test_cannot_assign_same_user_twice(self):
        self.authenticate_client()
        url = reverse('engagements:assignment-create')
        # First assignment
        response1 = self.client.post(url, self.assignment_data, format='json')
        self.assertIn(response1.status_code, (200, 201))
        # Duplicate assignment
        response2 = self.client.post(url, self.assignment_data, format='json')
        self.assertEqual(response2.status_code, 400)

    def test_unauthenticated_user_cannot_create_assignment(self):
        url = reverse('engagements:assignment-create')
        response = self.client.post(url, self.assignment_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_assignment_requires_valid_work_item_and_user(self):
        self.authenticate_client()
        url = reverse('engagements:assignment-create')
        # Invalid work_item
        data = self.assignment_data.copy()
        data['work_item'] = '00000000-0000-0000-0000-000000000000'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid user
        data = self.assignment_data.copy()
        data['user'] = 999999
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_assignment_scoped_to_tenant(self):
        self.authenticate_client()
        other_tenant = create_tenant()
        other_user = create_user(tenant=other_tenant, username='otheruser', email='otheruser@example.com')
        other_ticket = create_ticket(tenant=other_tenant, created_by=other_user)
        # Try to assign user from another tenant
        data = {
            'work_item': str(other_ticket.id),
            'user': other_user.id,
        }
        url = reverse('engagements:assignment-create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_assignment_assigned_by_is_set_to_request_user(self):
        self.authenticate_client()
        url = reverse('engagements:assignment-create')
        response = self.client.post(url, self.assignment_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        assignment = Assignment.objects.get(id=response.data['id'])
        self.assertEqual(assignment.assigned_by, self.user)

    def test_assignment_serializer_returns_expected_fields(self):
        self.authenticate_client()
        url = reverse('engagements:assignment-create')
        response = self.client.post(url, self.assignment_data, format='json')
        self.assertIn(response.status_code, (200, 201))
        self.assertIn('id', response.data)
        self.assertIn('user', response.data)
        self.assertIn('assigned_by', response.data)
        self.assertIn('assigned_at', response.data)
