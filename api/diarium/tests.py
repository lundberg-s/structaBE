from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from diarium.models import Case, Attachment, Comment, ActivityLog
import uuid

User = get_user_model()

class CaseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.case = Case.objects.create(
            title='Test Case',
            description='This is a test case',
            status='open',
            category='Bug',
            priority='medium',
            created_by=self.user
        )
    
    def test_case_creation(self):
        """Test that a case can be created"""
        self.assertEqual(self.case.title, 'Test Case')
        self.assertEqual(self.case.status, 'open')
        self.assertEqual(self.case.created_by, self.user)
        self.assertIsNotNone(self.case.id)
    
    def test_case_str_representation(self):
        """Test the string representation of a case"""
        expected = f"{self.case.title} - {self.case.status}"
        self.assertEqual(str(self.case), expected)
    
    def test_case_ordering(self):
        """Test that cases are ordered by creation date (newest first)"""
        case2 = Case.objects.create(
            title='Test Case 2',
            description='This is another test case',
            status='in-progress',
            category='Feature',
            priority='high',
            created_by=self.user
        )
        
        cases = Case.objects.all()
        self.assertEqual(cases[0], case2)  # Newest first
        self.assertEqual(cases[1], self.case)

class CaseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=self.user)
        
        self.case_data = {
            'title': 'Test Case',
            'description': 'This is a test case',
            'status': 'open',
            'category': 'Bug',
            'priority': 'medium'
        }
    
    def test_create_case(self):
        """Test creating a new case via API"""
        url = reverse('diarium:case-list')
        response = self.client.post(url, self.case_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Case.objects.count(), 1)
        
        case = Case.objects.first()
        self.assertEqual(case.title, 'Test Case')
        self.assertEqual(case.created_by, self.user)
        
        # Check that activity log was created
        self.assertEqual(ActivityLog.objects.count(), 1)
        activity = ActivityLog.objects.first()
        self.assertEqual(activity.activity_type, 'created')
    
    def test_list_cases(self):
        """Test listing all cases"""
        # Create a test case
        case = Case.objects.create(
            title='Test Case',
            description='This is a test case',
            status='open',
            category='Bug',
            priority='medium',
            created_by=self.user
        )
        
        url = reverse('diarium:case-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Case')
    
    def test_get_case_detail(self):
        """Test getting a specific case by ID"""
        case = Case.objects.create(
            title='Test Case',
            description='This is a test case',
            status='open',
            category='Bug',
            priority='medium',
            created_by=self.user
        )
        
        url = reverse('diarium:case-detail', kwargs={'id': case.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Case')
        self.assertEqual(response.data['id'], str(case.id))
    
    def test_update_case(self):
        """Test updating a case"""
        case = Case.objects.create(
            title='Test Case',
            description='This is a test case',
            status='open',
            category='Bug',
            priority='medium',
            created_by=self.user
        )
        
        update_data = {
            'title': 'Updated Test Case',
            'description': 'This is an updated test case',
            'status': 'in-progress',
            'category': 'Feature',
            'priority': 'high'
        }
        
        url = reverse('diarium:case-detail', kwargs={'id': case.id})
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        case.refresh_from_db()
        self.assertEqual(case.title, 'Updated Test Case')
        self.assertEqual(case.status, 'in-progress')
        
        # Check that activity log was created
        self.assertEqual(ActivityLog.objects.count(), 2)  # 1 for creation, 1 for update
    
    def test_delete_case(self):
        """Test deleting a case"""
        case = Case.objects.create(
            title='Test Case',
            description='This is a test case',
            status='open',
            category='Bug',
            priority='medium',
            created_by=self.user
        )
        
        url = reverse('diarium:case-detail', kwargs={'id': case.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Case.objects.count(), 0)
    
    def test_get_nonexistent_case(self):
        """Test getting a case that doesn't exist"""
        fake_id = uuid.uuid4()
        url = reverse('diarium:case-detail', kwargs={'id': fake_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access cases"""
        self.client.force_authenticate(user=None)
        
        url = reverse('diarium:case-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_case_with_assigned_user(self):
        """Test creating a case with an assigned user"""
        assigned_user = User.objects.create_user(
            username='assigneduser',
            email='assigned@example.com',
            password='testpass123'
        )
        
        case_data = {
            'title': 'Assigned Case',
            'description': 'This case is assigned to a user',
            'status': 'open',
            'category': 'Bug',
            'priority': 'medium',
            'assigned_user': assigned_user.id
        }
        
        url = reverse('diarium:case-list')
        response = self.client.post(url, case_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        case = Case.objects.first()
        self.assertEqual(case.assigned_user, assigned_user)
