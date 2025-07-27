from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import AuditLog, Tenant
from engagements.models import WorkItem, Ticket, Case, Job, Attachment, Comment, Assignment

User = get_user_model()


class EngagementsAdminAuditTestCase(TestCase):
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
        
        # Create a regular user
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123',
            tenant=self.tenant
        )

    def test_workitem_admin_audit_logging(self):
        """Test that WorkItem admin creates audit logs."""
        workitem = WorkItem.objects.create(
            tenant=self.tenant,
            title='Test Work Item',
            description='Test description',
            status='open',
            priority='medium'
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='workitem',
            entity_id=workitem.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Test Work Item')
        self.assertEqual(audit_log.business_process, 'General')

    def test_ticket_admin_audit_logging(self):
        """Test that Ticket admin creates audit logs."""
        ticket = Ticket.objects.create(
            tenant=self.tenant,
            title='Test Ticket',
            description='Test ticket description',
            urgency='medium',
            status='open'
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='ticket',
            entity_id=ticket.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Test Ticket')
        self.assertEqual(audit_log.business_process, 'Ticket Management')

    def test_case_admin_audit_logging(self):
        """Test that Case admin creates audit logs."""
        case = Case.objects.create(
            tenant=self.tenant,
            title='Test Case',
            description='Test case description',
            legal_area='civil',
            status='active'
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='case',
            entity_id=case.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Test Case')
        self.assertEqual(audit_log.business_process, 'Case Management')

    def test_job_admin_audit_logging(self):
        """Test that Job admin creates audit logs."""
        job = Job.objects.create(
            tenant=self.tenant,
            title='Test Job',
            description='Test job description',
            job_code='JOB-001',
            estimated_hours=10,
            status='pending'
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='job',
            entity_id=job.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'Test Job')
        self.assertEqual(audit_log.business_process, 'Job Management')

    def test_attachment_admin_audit_logging(self):
        """Test that Attachment admin creates audit logs."""
        workitem = WorkItem.objects.create(
            tenant=self.tenant,
            title='Test Work Item',
            status='open'
        )
        
        attachment = Attachment.objects.create(
            tenant=self.tenant,
            work_item=workitem,
            filename='test.pdf',
            file_size=1024,
            mime_type='application/pdf'
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='attachment',
            entity_id=attachment.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'test.pdf')
        self.assertEqual(audit_log.business_process, 'Document Management')

    def test_comment_admin_audit_logging(self):
        """Test that Comment admin creates audit logs."""
        workitem = WorkItem.objects.create(
            tenant=self.tenant,
            title='Test Work Item',
            status='open'
        )
        
        comment = Comment.objects.create(
            tenant=self.tenant,
            work_item=workitem,
            content='Test comment content',
            created_by=self.user
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='comment',
            entity_id=comment.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.business_process, 'Communication Management')

    def test_assignment_admin_audit_logging(self):
        """Test that Assignment admin creates audit logs."""
        workitem = WorkItem.objects.create(
            tenant=self.tenant,
            title='Test Work Item',
            status='open'
        )
        
        assignment = Assignment.objects.create(
            tenant=self.tenant,
            work_item=workitem,
            user=self.user
        )
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='assignment',
            entity_id=assignment.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.business_process, 'Resource Management')

    def test_engagements_admin_update_audit_logging(self):
        """Test that engagements admin creates audit logs for updates."""
        workitem = WorkItem.objects.create(
            tenant=self.tenant,
            title='Test Work Item',
            status='open'
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Update the work item
        workitem.title = 'Updated Work Item'
        workitem.status = 'closed'
        workitem.save()
        
        # Check that audit log was created for update
        audit_logs = AuditLog.objects.filter(
            entity_type='workitem',
            entity_id=workitem.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'updated')
        self.assertEqual(audit_log.entity_name, 'Updated Work Item')

    def test_engagements_admin_delete_audit_logging(self):
        """Test that engagements admin creates audit logs for deletions."""
        workitem = WorkItem.objects.create(
            tenant=self.tenant,
            title='Test Work Item',
            status='open'
        )
        
        # Clear existing audit logs
        AuditLog.objects.all().delete()
        
        # Delete the work item
        workitem.delete()
        
        # Check that audit log was created for deletion
        audit_logs = AuditLog.objects.filter(
            entity_type='workitem',
            entity_id=workitem.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'deleted')
        self.assertEqual(audit_log.risk_level, 'high') 