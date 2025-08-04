
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from core.models import AuditLog, Tenant
from engagements.models import WorkItem, Ticket, Case, Job, Attachment, Comment
from engagements.admin import WorkItemAdmin, TicketAdmin, CaseAdmin, JobAdmin, AttachmentAdmin, CommentAdmin
from engagements.tests.test_helper import EngagementsTestHelper
from engagements.tests.test_constants import WorkItemType, TestData

User = get_user_model()


class EngagementsAdminAuditTestCase(EngagementsTestHelper):
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
        # Create a tenant
        self.tenant = self.create_tenant(work_item_type=WorkItemType.TICKET)
        
        # Create a superuser with proper Person/Role setup
        self.superuser = self.create_user(
            email='admin@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        # Make superuser
        self.superuser.is_staff = True
        self.superuser.is_superuser = True
        self.superuser.save()
        
        # Create a regular user with proper Person/Role setup
        self.user = self.create_user(
            email='user@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        # Set up admin site and request factory
        self.admin_site = AdminSite()
        self.request_factory = RequestFactory()
        
        # Create admin instances
        self.workitem_admin = WorkItemAdmin(WorkItem, self.admin_site)
        self.ticket_admin = TicketAdmin(Ticket, self.admin_site)
        self.case_admin = CaseAdmin(Case, self.admin_site)
        self.job_admin = JobAdmin(Job, self.admin_site)
        self.attachment_admin = AttachmentAdmin(Attachment, self.admin_site)
        self.comment_admin = CommentAdmin(Comment, self.admin_site)

    def _create_request(self, user=None):
        """Create a mock request for admin operations."""
        if user is None:
            user = self.superuser
        
        request = self.request_factory.post('/admin/')
        request.user = user
        request.session = {}
        return request

    def test_workitem_admin_audit_logging(self):
        """Test that WorkItem admin creates audit logs."""
        # Create workitem through admin
        workitem = WorkItem(
            tenant=self.tenant,
            title='Test Work Item',
            description='Test description',
            status=self.create_work_item_statuses(amount=1)[0],
            category=self.create_work_item_categories(amount=1)[0],
            priority=self.create_work_item_priorities(amount=1)[0],
            created_by=self.superuser.id
        )
        
        request = self._create_request()
        self.workitem_admin.save_model(request, workitem, None, change=False)
        
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
        # Create ticket through admin
        ticket = Ticket(
            tenant=self.tenant,
            title='Test Ticket',
            description='Test ticket description',
            priority=self.create_work_item_priorities(amount=1)[0],
            status=self.create_work_item_statuses(amount=1)[0],
            category=self.create_work_item_categories(amount=1)[0],
            created_by=self.superuser.id
        )
        
        request = self._create_request()
        self.ticket_admin.save_model(request, ticket, None, change=False)
        
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
        # Create case through admin
        case = Case(
            tenant=self.tenant,
            title='Test Case',
            description='Test case description',
            legal_area='civil',
            status=self.create_work_item_statuses(amount=1)[0],
            category=self.create_work_item_categories(amount=1)[0],
            priority=self.create_work_item_priorities(amount=1)[0],
            created_by=self.superuser.id
        )
        
        request = self._create_request()
        self.case_admin.save_model(request, case, None, change=False)
        
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
        # Create job through admin
        job = Job(
            tenant=self.tenant,
            title='Test Job',
            description='Test job description',
            job_code='JOB-001',
            estimated_hours=10,
            status=self.create_work_item_statuses(amount=1)[0],
            category=self.create_work_item_categories(amount=1)[0],
            priority=self.create_work_item_priorities(amount=1)[0],
            created_by=self.superuser.id
        )
        
        request = self._create_request()
        self.job_admin.save_model(request, job, None, change=False)
        
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
        # Create workitem through admin first
        workitem = WorkItem(
            tenant=self.tenant,
            title='Test Work Item',
            status=self.create_work_item_statuses(amount=1)[0],
            category=self.create_work_item_categories(amount=1)[0],
            priority=self.create_work_item_priorities(amount=1)[0],
            created_by=self.superuser.id
        )
        
        request = self._create_request()
        self.workitem_admin.save_model(request, workitem, None, change=False)
        
        # Create attachment through admin
        attachment = Attachment(
            tenant=self.tenant,
            work_item=workitem,
            filename='test.pdf',
            file_size=1024,
            mime_type='application/pdf',
            created_by=self.superuser.id
        )
        
        self.attachment_admin.save_model(request, attachment, None, change=False)
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='attachment',
            entity_id=attachment.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.entity_name, 'test.pdf attached to Test Work Item')
        self.assertEqual(audit_log.business_process, 'Document Management')

    def test_comment_admin_audit_logging(self):
        """Test that Comment admin creates audit logs."""
        # Create workitem through admin first
        workitem = WorkItem(
            tenant=self.tenant,
            title='Test Work Item',
            status=self.create_work_item_statuses(amount=1)[0],
            category=self.create_work_item_categories(amount=1)[0],
            priority=self.create_work_item_priorities(amount=1)[0],
            created_by=self.superuser.id
        )
        
        request = self._create_request()
        self.workitem_admin.save_model(request, workitem, None, change=False)
        
        # Create comment through admin
        comment = Comment(
            tenant=self.tenant,
            work_item=workitem,
            content='Test comment content',
            created_by=self.user.id
        )
        
        self.comment_admin.save_model(request, comment, None, change=False)
        
        # Check that audit log was created
        audit_logs = AuditLog.objects.filter(
            entity_type='comment',
            entity_id=comment.id
        )
        self.assertEqual(audit_logs.count(), 1)
        
        audit_log = audit_logs.first()
        self.assertEqual(audit_log.activity_type, 'created')
        self.assertEqual(audit_log.business_process, 'Communication Management')

    # def test_assignment_admin_audit_logging(self):
    #     """Test that Assignment admin creates audit logs."""
    #     workitem = self.factory.create_work_item('ticket')
        
    #     assignment = Assignment.objects.create(
    #         tenant=self.tenant,
    #         work_item=workitem,
    #         user=self.user
    #     )
        
    #     # Check that audit log was created
    #     audit_logs = AuditLog.objects.filter(
    #         entity_type='assignment',
    #         entity_id=assignment.id
    #     )
    #     self.assertEqual(audit_logs.count(), 1)
        
    #     audit_log = audit_logs.first()
    #     self.assertEqual(audit_log.activity_type, 'created')
    #     self.assertEqual(audit_log.business_process, 'Resource Management')

    # def test_engagements_admin_update_audit_logging(self):
    #     """Test that engagements admin creates audit logs for updates."""
    #     workitem = self.factory.create_work_item('ticket')
        
    #     # Clear existing audit logs
    #     AuditLog.objects.all().delete()
        
    #     # Update the work item
    #     workitem.title = 'Updated Work Item'
    #     workitem.status = 'closed'
    #     workitem.save()
        
    #     # Check that audit log was created for update
    #     audit_logs = AuditLog.objects.filter(
    #         entity_type='workitem',
    #         entity_id=workitem.id
    #     )
    #     self.assertEqual(audit_logs.count(), 1)
        
    #     audit_log = audit_logs.first()
    #     self.assertEqual(audit_log.activity_type, 'updated')
    #     self.assertEqual(audit_log.entity_name, 'Updated Work Item')

    # def test_engagements_admin_delete_audit_logging(self):
    #     """Test that engagements admin creates audit logs for deletions."""
    #     workitem = self.factory.create_work_item('ticket')
        
    #     # Clear existing audit logs
    #     AuditLog.objects.all().delete()
        
    #     # Delete the work item
    #     workitem.delete()
        
    #     # Check that audit log was created for deletion
    #     audit_logs = AuditLog.objects.filter(
    #         entity_type='workitem',
    #         entity_id=workitem.id
    #     )
    #     self.assertEqual(audit_logs.count(), 1)
        
    #     audit_log = audit_logs.first()
    #     self.assertEqual(audit_log.activity_type, 'deleted')
    #     self.assertEqual(audit_log.risk_level, 'high') 