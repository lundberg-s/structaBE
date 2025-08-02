from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from core.models import AuditLog, Tenant, Role
from core.admin import TenantAdmin, RoleAdmin

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
        
        # Set up admin site and request factory
        self.admin_site = AdminSite()
        self.request_factory = RequestFactory()
        
        # Create admin instances
        self.tenant_admin = TenantAdmin(Tenant, self.admin_site)
        self.role_admin = RoleAdmin(Role, self.admin_site)

    def _create_request(self, user=None):
        """Create a mock request for admin operations."""
        if user is None:
            user = self.superuser
        
        request = self.request_factory.post('/admin/')
        request.user = user
        request.session = {}
        return request

    def test_tenant_admin_audit_logging(self):
        """Test that Tenant admin creates audit logs."""
        # Create tenant through admin
        tenant = Tenant(
            subscription_plan='premium',
            subscription_status='active',
            billing_email='billing@example.com'
        )
        
        request = self._create_request()
        self.tenant_admin.save_model(request, tenant, None, change=False)
        
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
        # Create tenant through admin
        tenant = Tenant(
            subscription_plan='basic',
            subscription_status='trial'
        )
        
        request = self._create_request()
        self.tenant_admin.save_model(request, tenant, None, change=False)
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the tenant through admin
        tenant.subscription_plan = 'premium'
        tenant.subscription_status = 'active'
        self.tenant_admin.save_model(request, tenant, None, change=True)
        
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
        # Create tenant through admin
        tenant = Tenant(
            subscription_plan='basic',
            subscription_status='trial'
        )
        
        request = self._create_request()
        self.tenant_admin.save_model(request, tenant, None, change=False)
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Store tenant ID before deletion
        tenant_id = str(tenant.id)
        
        # Delete the tenant through admin
        self.tenant_admin.delete_model(request, tenant)
        
        # Check that audit log was created for deletion
        # After deletion, we need to look for audit logs by entity_type and entity_name
        # since the tenant.id might not be available after deletion
        audit_logs = AuditLog.objects.filter(
            entity_type='tenant',
            entity_name=tenant_id  # Use stored tenant ID
        )
        

        
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'deleted')
        self.assertEqual(audit_log.risk_level, 'high')

    def test_role_admin_audit_logging(self):
        """Test that Role admin creates audit logs."""
        # Create role through admin
        role = Role(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        request = self._create_request()
        self.role_admin.save_model(request, role, None, change=False)
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Test Role')  # Using label, not key
        self.assertEqual(audit_log.business_process, 'Access Management')

    def test_role_admin_update_audit_logging(self):
        """Test that Role admin creates audit logs for updates."""
        # Create role through admin
        role = Role(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        request = self._create_request()
        self.role_admin.save_model(request, role, None, change=False)
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the role through admin
        role.label = 'Updated Test Role'
        self.role_admin.save_model(request, role, None, change=True)
        
        # Check that audit log was created for update
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'updated')
        self.assertEqual(audit_log.entity_name, 'Updated Test Role')  # Using updated label

    def test_role_admin_delete_audit_logging(self):
        """Test that Role admin creates audit logs for deletions."""
        # Create role through admin
        role = Role(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        request = self._create_request()
        self.role_admin.save_model(request, role, None, change=False)
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Delete the role through admin
        self.role_admin.delete_model(request, role)
        
        # Check that audit log was created for deletion
        # After deletion, we need to look for audit logs by entity_type and entity_name
        # since the role.id might not be available after deletion
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_name='Test Role'  # This should match the role.label
        )

        
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'deleted')
        self.assertEqual(audit_log.risk_level, 'high')

    def test_system_role_admin_audit_logging(self):
        """Test that system role creation is also logged."""
        # Create system role through admin
        role = Role(
            tenant=None,  # System roles don't have tenants
            key='admin',
            label='Admin',
            is_system=True
        )
        
        request = self._create_request()
        self.role_admin.save_model(request, role, None, change=False)
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Admin')  # Using label, not key
        # System roles get assigned to a system tenant for audit purposes
        self.assertIsNotNone(audit_log.tenant) 