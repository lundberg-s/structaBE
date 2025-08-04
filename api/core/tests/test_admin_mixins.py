from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from core.models import Tenant, Role, AuditLog
from partners.models import Organization
from core.admin import TenantAdmin, RoleAdmin
from partners.admin import OrganizationAdmin

User = get_user_model()


class AdminAuditMixinTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.tenant = Tenant.objects.create()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create admin instances
        self.admin_site = AdminSite()
        self.tenant_admin = TenantAdmin(Role, self.admin_site)
        self.role_admin = RoleAdmin(Role, self.admin_site)
        self.org_admin = OrganizationAdmin(Organization, self.admin_site)

    def test_audit_mixin_creates_log_on_save(self):
        """Test that AdminAuditMixin creates audit logs when saving models."""
        # Create an organization through admin
        org = Organization(
            tenant=self.tenant,
            name='Test Organization',
            organization_number='ORG-001'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Test Organization')
        self.assertEqual(audit_log.tenant, self.tenant)
        self.assertEqual(audit_log.business_process, 'Partner Management')

    def test_audit_mixin_creates_log_on_update(self):
        """Test that AdminAuditMixin creates audit logs when updating models."""
        # Create an organization through admin
        org = Organization(
            tenant=self.tenant,
            name='Test Organization',
            organization_number='ORG-001'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the organization through admin
        org.name = 'Updated Organization'
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=True
        )
        
        # Check that audit log was created for update
        audit_logs = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'updated')
        self.assertEqual(audit_log.entity_name, 'Updated Organization')

    def test_audit_mixin_creates_log_on_delete(self):
        """Test that AdminAuditMixin creates audit logs when deleting models."""
        # Create an organization through admin
        org = Organization(
            tenant=self.tenant,
            name='Test Organization',
            organization_number='ORG-001'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Delete the organization through admin
        self.org_admin.delete_model(
            request=self._create_request(),
            obj=org
        )
        
        # Check that audit log was created for deletion
        audit_logs = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'deleted')
        self.assertEqual(audit_log.risk_level, 'high')

    def test_audit_mixin_entity_type_mapping(self):
        """Test that AdminAuditMixin correctly maps entity types."""
        # Test different model types through admin
        role = Role(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        # Simulate admin save
        self.role_admin.save_model(
            request=self._create_request(),
            obj=role,
            form=None,
            change=False
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.entity_type, 'role')

    def test_audit_mixin_risk_level_assessment(self):
        """Test that AdminAuditMixin correctly assesses risk levels."""
        # Test low risk (create)
        org = Organization(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.risk_level, 'low')

    def test_audit_mixin_compliance_category(self):
        """Test that AdminAuditMixin correctly assigns compliance categories."""
        # Test privacy category for organization
        org = Organization(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.compliance_category, 'privacy')

    def test_audit_mixin_business_process_mapping(self):
        """Test that AdminAuditMixin correctly maps business processes."""
        # Test business process mapping
        org = Organization(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.business_process, 'Partner Management')

    def test_audit_mixin_entity_name_extraction(self):
        """Test that AdminAuditMixin correctly extracts entity names."""
        # Test entity name extraction
        org = Organization(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        # Simulate admin save
        self.org_admin.save_model(
            request=self._create_request(),
            obj=org,
            form=None,
            change=False
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.entity_name, 'Test Organization')

    def _create_request(self):
        """Create a mock request for admin operations."""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = self.user
        request.session = {}
        return request 