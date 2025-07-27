from django.test import TestCase
from rest_framework.exceptions import ValidationError
from engagements.utilities.assignment_utilities import (
    update_work_item_assignments,
    _remove_assignments,
    _add_assignments
)
from engagements.tests.factory import create_ticket
from relations.tests.factory import create_user
from relations.tests.factory import create_tenant, create_person
from engagements.models import Assignment
from users.models import User


class TestAssignmentUtilities(TestCase):
    """Test the assignment utilities functions."""
    
    def setUp(self):
        self.tenant = create_tenant()
        self.created_by_user = create_user(self.tenant)
        self.work_item = create_ticket(tenant=self.tenant, created_by=self.created_by_user)
        
        # Create test users
        person1 = create_person(self.tenant)
        person2 = create_person(self.tenant)
        person3 = create_person(self.tenant)
        
        self.user1 = create_user(self.tenant)
        self.user1.partner = person1
        self.user1.save()
        
        self.user2 = create_user(self.tenant)
        self.user2.partner = person2
        self.user2.save()
        
        self.user3 = create_user(self.tenant)
        self.user3.partner = person3
        self.user3.save()
    
    def test_update_work_item_assignments_add_new_users(self):
        """Test adding new users to work item assignments."""
        new_user_ids = [self.user1.id, self.user2.id]
        
        update_work_item_assignments(self.work_item, new_user_ids, self.created_by_user)
        
        # Check that assignments were created
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 2)
        
        assigned_user_ids = set(assignments.values_list('user_id', flat=True))
        self.assertEqual(assigned_user_ids, set(new_user_ids))
    
    def test_update_work_item_assignments_remove_users(self):
        """Test removing users from work item assignments."""
        # First add some users
        initial_user_ids = [self.user1.id, self.user2.id, self.user3.id]
        update_work_item_assignments(self.work_item, initial_user_ids, self.created_by_user)
        
        # Then remove some users
        new_user_ids = [self.user1.id]  # Only keep user1
        update_work_item_assignments(self.work_item, new_user_ids, self.created_by_user)
        
        # Check that only user1 remains assigned
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().user_id, self.user1.id)
    
    def test_update_work_item_assignments_replace_users(self):
        """Test replacing all users with new ones."""
        # First add some users
        initial_user_ids = [self.user1.id, self.user2.id]
        update_work_item_assignments(self.work_item, initial_user_ids, self.created_by_user)
        
        # Then replace with different users
        new_user_ids = [self.user3.id]
        update_work_item_assignments(self.work_item, new_user_ids, self.created_by_user)
        
        # Check that only user3 is assigned
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().user_id, self.user3.id)
    
    def test_update_work_item_assignments_no_changes(self):
        """Test when no changes are needed."""
        # Add users
        user_ids = [self.user1.id, self.user2.id]
        update_work_item_assignments(self.work_item, user_ids, self.created_by_user)
        
        # Update with same users
        update_work_item_assignments(self.work_item, user_ids, self.created_by_user)
        
        # Check that assignments remain the same
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 2)
    
    def test_update_work_item_assignments_empty_list(self):
        """Test removing all users."""
        # First add some users
        initial_user_ids = [self.user1.id, self.user2.id]
        update_work_item_assignments(self.work_item, initial_user_ids, self.created_by_user)
        
        # Then remove all users
        update_work_item_assignments(self.work_item, [], self.created_by_user)
        
        # Check that no assignments remain
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 0)
    
    def test_add_assignments_success(self):
        """Test successfully adding assignments."""
        user_ids = [self.user1.id, self.user2.id]
        
        _add_assignments(self.work_item, user_ids, self.created_by_user)
        
        # Check that assignments were created
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 2)
        
        for assignment in assignments:
            self.assertEqual(assignment.created_by, self.created_by_user)
            self.assertEqual(assignment.work_item.id, self.work_item.id)
    
    def test_add_assignments_invalid_user_id(self):
        """Test adding assignments with invalid user ID."""
        invalid_user_id = 99999  # Non-existent user ID
        user_ids = [self.user1.id, invalid_user_id]
        
        with self.assertRaises(ValidationError) as cm:
            _add_assignments(self.work_item, user_ids, self.created_by_user)
        
        self.assertIn("User(s) with ID(s)", str(cm.exception))
        self.assertIn(str(invalid_user_id), str(cm.exception))
    
    def test_add_assignments_user_from_different_tenant(self):
        """Test adding assignments with user from different tenant."""
        other_tenant = create_tenant()
        other_user = create_user(other_tenant)
        
        user_ids = [self.user1.id, other_user.id]
        
        with self.assertRaises(ValidationError) as cm:
            _add_assignments(self.work_item, user_ids, self.created_by_user)
        
        self.assertIn("User(s) with ID(s)", str(cm.exception))
        self.assertIn(str(other_user.id), str(cm.exception))
    
    def test_remove_assignments(self):
        """Test removing assignments."""
        # First add some assignments
        user_ids = [self.user1.id, self.user2.id, self.user3.id]
        _add_assignments(self.work_item, user_ids, self.created_by_user)
        
        # Then remove some
        users_to_remove = [self.user1.id, self.user2.id]
        _remove_assignments(self.work_item, users_to_remove)
        
        # Check that only user3 remains
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().user_id, self.user3.id)
    
    def test_remove_assignments_nonexistent(self):
        """Test removing assignments that don't exist."""
        # Add one assignment
        _add_assignments(self.work_item, [self.user1.id], self.created_by_user)
        
        # Try to remove non-existent assignment
        _remove_assignments(self.work_item, [99999])  # Non-existent user ID
        
        # Check that the original assignment still exists
        assignments = Assignment.objects.filter(work_item=self.work_item)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().user_id, self.user1.id) 