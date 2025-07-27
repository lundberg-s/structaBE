from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import AuditLog, Tenant, Role
from core.admin_mixins import AdminAuditMixin
from relations.models import Organization

User = get_user_model()


class AdminAuditMixinTestCase(TestCase):
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

    def test_audit_mixin_creates_log_on_save(self):
        """Test that AdminAuditMixin creates audit logs when saving models."""
        # Test with Organization model
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization',
            organization_number='ORG-001'
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
        # Create an organization
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization',
            organization_number='ORG-001'
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the organization
        org.name = 'Updated Organization'
        org.save()
        
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
        # Create an organization
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization',
            organization_number='ORG-001'
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Delete the organization
        org.delete()
        
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
        # Test different model types
        role = Role.objects.create(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
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
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertEqual(audit_log.risk_level, 'low')
        
        # Test high risk (delete)
        org.delete()
        
        delete_audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id,
            activity_type='deleted'
        ).first()
        
        self.assertEqual(delete_audit_log.risk_level, 'high')

    def test_audit_mixin_compliance_category(self):
        """Test that AdminAuditMixin correctly assigns compliance categories."""
        # Test privacy category for person/organization
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertEqual(audit_log.compliance_category, 'privacy')

    def test_audit_mixin_business_process_mapping(self):
        """Test that AdminAuditMixin correctly maps business processes."""
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertEqual(audit_log.business_process, 'Partner Management')

    def test_audit_mixin_entity_name_extraction(self):
        """Test that AdminAuditMixin correctly extracts entity names."""
        # Test organization with name
        org = Organization.objects.create(
            tenant=self.tenant,
            name='Test Organization'
        )
        
        audit_log = AuditLog.objects.filter(
            entity_type='organization',
            entity_id=org.id
        ).first()
        
        self.assertEqual(audit_log.entity_name, 'Test Organization')
        
        # Test role with key
        role = Role.objects.create(
            tenant=self.tenant,
            key='test_role',
            label='Test Role',
            is_system=False
        )
        
        role_audit_log = AuditLog.objects.filter(
            entity_type='role',
            entity_id=role.id
        ).first()
        
        self.assertEqual(role_audit_log.entity_name, 'test_role') 