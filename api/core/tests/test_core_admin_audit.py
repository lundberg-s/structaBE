from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import AuditLog, Tenant, Role
from core.admin_mixins import AdminAuditMixin

User = get_user_model()


class CoreAdminAuditTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a tenant
        self.tenant = Tenant.objects.create()
        
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            tenant=self.tenant
        )

    def test_tenant_admin_audit_logging(self):
        """Test that Tenant admin creates audit logs."""
        tenant = Tenant.objects.create(
            subscription_plan='premium',
            subscription_status='active',
            billing_email='billing@example.com'
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='tenant',
            entity_id=tenant.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.compliance_category, 'security')
        self.assertEqual(audit_log.business_process, 'Access Management')

    def test_tenant_admin_update_audit_logging(self):
        """Test that Tenant admin creates audit logs for updates."""
        tenant = Tenant.objects.create(
            subscription_plan='basic',
            subscription_status='trial'
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the tenant
        tenant.subscription_plan = 'premium'
        tenant.subscription_status = 'active'
        tenant.save()
        
        # Check that audit log was created for update
        audit_logs = AuditLog.objects.filter(
            entity_type='tenant',
            entity_id=tenant.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'updated')
        self.assertEqual(audit_log.compliance_category, 'security')

    def test_tenant_admin_delete_audit_logging(self):
        """Test that Tenant admin creates audit logs for deletions."""
        tenant = Tenant.objects.create(
            subscription_plan='basic',
            subscription_status='trial'
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Delete the tenant
        tenant.delete()
        
        # Check that audit log was created for deletion
        audit_logs = AuditLog.objects.filter(
            entity_type='tenant',
            entity_id=tenant.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'deleted')
        self.assertEqual(audit_log.risk_level, 'high')

    def test_role_admin_audit_logging(self):
        """Test that Role admin creates audit logs."""
        role = Role.objects.create(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'test_role')
        self.assertEqual(audit_log.business_process, 'Access Management')

    def test_role_admin_update_audit_logging(self):
        """Test that Role admin creates audit logs for updates."""
        role = Role.objects.create(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the role
        role.label = 'Updated Test Role'
        role.save()
        
        # Check that audit log was created for update
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'updated')
        self.assertEqual(audit_log.entity_name, 'test_role')

    def test_role_admin_delete_audit_logging(self):
        """Test that Role admin creates audit logs for deletions."""
        role = Role.objects.create(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Delete the role
        role.delete()
        
        # Check that audit log was created for deletion
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'deleted')
        self.assertEqual(audit_log.risk_level, 'high')

    def test_system_role_admin_audit_logging(self):
        """Test that system role creation is also logged."""
        role = Role.objects.create(
            tenant=None,  # System roles don't have tenants
            key='system_role',
            label='System Role',
            is_system=True
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'system_role')
        self.assertIsNone(audit_log.tenant)  # System roles have no tenant 