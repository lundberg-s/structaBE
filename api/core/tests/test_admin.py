from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import AuditLog, Tenant
from core.admin import AuditLogAdmin

User = get_user_model()


class AuditLogAdminTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create a tenant
        self.tenant = Tenant.objects.create()
        
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        # Create a regular user
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        # Create some audit logs
        self.audit_log1 = AuditLog.objects.create(
            tenant=self.tenant,
            entity_type='ticket',
            entity_id='12345678-1234-1234-1234-123456789012',
            entity_name='Test Ticket',
            created_by=self.user,
            activity_type='created',
            description='Test ticket was created',
            risk_level='low',
            compliance_category='operational'
        )
        
        self.audit_log2 = AuditLog.objects.create(
            tenant=self.tenant,
            entity_type='person',
            entity_id='87654321-4321-4321-4321-210987654321',
            entity_name='John Doe',
            created_by=self.superuser,
            activity_type='deleted',
            description='Person record was deleted',
            risk_level='high',
            compliance_category='privacy'
        )

    def test_audit_log_admin_list_view(self):
        """Test that the audit log admin list view is accessible."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ticket')
        self.assertContains(response, 'John Doe')

    def test_audit_log_admin_detail_view(self):
        """Test that the audit log admin detail view is accessible."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_change', args=[self.audit_log1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ticket')
        self.assertContains(response, 'created')

    def test_audit_log_admin_no_add_permission(self):
        """Test that audit logs cannot be added through admin."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_add')
        response = self.client.get(url)
        
        # Should redirect to list view since add is not allowed
        self.assertEqual(response.status_code, 302)

    def test_audit_log_admin_no_change_permission(self):
        """Test that audit logs cannot be changed through admin."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_change', args=[self.audit_log1.id])
        response = self.client.post(url, {
            'description': 'Modified description'
        })
        
        # Should not allow changes
        self.assertEqual(response.status_code, 200)

    def test_audit_log_admin_no_delete_permission(self):
        """Test that audit logs cannot be deleted through admin."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_delete', args=[self.audit_log1.id])
        response = self.client.get(url)
        
        # Should redirect to list view since delete is not allowed
        self.assertEqual(response.status_code, 302)

    def test_audit_log_admin_export_action(self):
        """Test the export audit logs action."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_changelist')
        
        # Select audit logs and export
        response = self.client.post(url, {
            'action': 'export_audit_logs',
            '_selected_action': [self.audit_log1.id, self.audit_log2.id]
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_audit_log_admin_risk_level_badge(self):
        """Test the risk level badge display method."""
        admin = AuditLogAdmin(AuditLog, None)
        
        # Test low risk
        badge = admin.risk_level_badge(self.audit_log1)
        self.assertIn('green', str(badge))
        self.assertIn('LOW', str(badge))
        
        # Test high risk
        badge = admin.risk_level_badge(self.audit_log2)
        self.assertIn('red', str(badge))
        self.assertIn('HIGH', str(badge))

    def test_audit_log_admin_created_by_username(self):
        """Test the created by username display method."""
        admin = AuditLogAdmin(AuditLog, None)
        
        username_display = admin.created_by_username(self.audit_log1)
        self.assertIn('user', str(username_display))
        
        # Test with no user
        audit_log_no_user = AuditLog.objects.create(
            tenant=self.tenant,
            entity_type='ticket',
            entity_id='11111111-1111-1111-1111-111111111111',
            entity_name='No User Ticket',
            created_by=None,
            activity_type='created',
            description='Ticket created without user',
            risk_level='low',
            compliance_category='operational'
        )
        
        username_display = admin.created_by_username(audit_log_no_user)
        self.assertEqual(username_display, '-')

    def test_audit_log_admin_search(self):
        """Test that search functionality works."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_changelist')
        
        # Search by entity name
        response = self.client.get(url, {'q': 'Test Ticket'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ticket')
        self.assertNotContains(response, 'John Doe')
        
        # Search by activity type
        response = self.client.get(url, {'q': 'deleted'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Test Ticket')

    def test_audit_log_admin_filtering(self):
        """Test that filtering functionality works."""
        self.client.force_login(self.superuser)
        url = reverse('admin:core_auditlog_changelist')
        
        # Filter by risk level
        response = self.client.get(url, {'risk_level': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Test Ticket')
        
        # Filter by entity type
        response = self.client.get(url, {'entity_type': 'ticket'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ticket')
        self.assertNotContains(response, 'John Doe') 