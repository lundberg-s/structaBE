import mimetypes
import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from core.models import Tenant, AuditModel

User = get_user_model()

class WorkItemStatusTypes(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in-progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'

class WorkItemPriorityTypes(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'

class WorkItemCategoryTypes(models.TextChoices):
    TICKET = 'ticket', 'Ticket'
    CASE = 'case', 'Case'
    JOB = 'job', 'Job'

class WorkItemPartnerRoleTypes(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    VENDOR = 'vendor', 'Vendor'
    PLAINTIFF = 'plaintiff', 'Plaintiff'
    DEFENDANT = 'defendant', 'Defendant'

class ActivityLogActivityTypes(models.TextChoices):
    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    STATUS_CHANGED = 'status-changed', 'Status Changed'
    PRIORITY_CHANGED = 'priority-changed', 'Priority Changed'
    DEADLINE_CHANGED = 'deadline-changed', 'Deadline Changed'
    ASSIGNED = 'assigned', 'Assigned'
    COMMENTED = 'commented', 'Commented'
    ATTACHMENT_ADDED = 'attachment-added', 'Attachment Added'

class WorkItemQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)
    
    def all_with_deleted(self):
        return self.all()

    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related(
            'tenant',
            'created_by'
        ).prefetch_related(
            'attachments',
            'comments',
            'assignments',
            'activity_log',
            'partner_roles'
        )

    def by_tenant(self, tenant):
        """Get work items for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_status(self, status):
        """Get work items by status with optimized queries."""
        return self.filter(status=status).with_details()

    def by_category(self, category):
        """Get work items by category with optimized queries."""
        return self.filter(category=category).with_details()

    def by_priority(self, priority):
        """Get work items by priority with optimized queries."""
        return self.filter(priority=priority).with_details()

    def by_author(self, author):
        """Get work items by author with optimized queries."""
        return self.filter(created_by=author).with_details()

    def overdue(self):
        """Get overdue work items with optimized queries."""
        from django.utils import timezone
        return self.filter(
            deadline__lt=timezone.now(),
            status__in=['open', 'in-progress']
        ).with_details()

    def due_soon(self, days=7):
        """Get work items due soon with optimized queries."""
        from django.utils import timezone
        from datetime import timedelta
        future_date = timezone.now() + timedelta(days=days)
        return self.filter(
            deadline__lte=future_date,
            deadline__gt=timezone.now(),
            status__in=['open', 'in-progress']
        ).with_details()

class WorkItem(AuditModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='work_items')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=WorkItemStatusTypes.choices, default=WorkItemStatusTypes.OPEN)
    category = models.CharField(max_length=100, choices=WorkItemCategoryTypes.choices)
    priority = models.CharField(max_length=20, choices=WorkItemPriorityTypes.choices, default=WorkItemPriorityTypes.MEDIUM)
    deadline = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_work_items')
    is_deleted = models.BooleanField(default=False)

    objects = WorkItemQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['created_at']),
            models.Index(fields=['deadline']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['tenant', 'priority']),
            models.Index(fields=['tenant', 'is_deleted']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'status']),
        ]

    def get_real_instance(self):
        if hasattr(self, 'ticket'):
            return self.ticket
        if hasattr(self, 'case'):
            return self.case
        if hasattr(self, 'job'):
            return self.job
        return self

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    @property
    def assigned_to(self):
        """Get all users assigned to this work item"""
        # Use prefetched data if available
        if hasattr(self, '_prefetched_objects_cache') and 'assignments' in self._prefetched_objects_cache:
            return [assignment.user for assignment in self._prefetched_objects_cache['assignments']]
        # Fallback to database query
        return [assignment.user for assignment in self.assignments.all()]
        
class Ticket(WorkItem):
    ticket_number = models.CharField(max_length=50, null=True, blank=True)
    reported_by = models.CharField(max_length=255, null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=WorkItemPriorityTypes.choices, default=WorkItemPriorityTypes.MEDIUM)
    # entity: typically the customer or reporter
    pass

class Case(WorkItem):
    case_reference = models.CharField(max_length=100, unique=True)
    legal_area = models.CharField(max_length=100)
    court_date = models.DateField(null=True, blank=True)
    # entity: could be a person, organization, or other partner involved
    pass

class Job(WorkItem):
    job_code = models.CharField(max_length=50, unique=True)
    assigned_team = models.CharField(max_length=100)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    # entity: typically the customer or client for whom the job is performed
    pass

class WorkItemPartnerRole(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='work_item_partner_roles')
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='partner_roles')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    partner = GenericForeignKey('content_type', 'object_id')
    role = models.CharField(max_length=20, choices=WorkItemPartnerRoleTypes.choices)

    class Meta:
        unique_together = ('work_item', 'content_type', 'object_id', 'role', 'tenant')
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['work_item']),
            models.Index(fields=['role']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['tenant', 'work_item']),
            models.Index(fields=['tenant', 'role']),
        ]

    def __str__(self):
        return f"{self.partner} as {self.role} for {self.work_item}"

class Attachment(AuditModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attachments')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='case_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.file and self.file.name and not self.mime_type:
            mime, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime or ''
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"{self.filename} - {self.work_item.title}"

    class Meta:
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['work_item']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['filename']),
            models.Index(fields=['mime_type']),
            models.Index(fields=['tenant', 'work_item']),
            models.Index(fields=['uploaded_by', 'created_at']),
        ]

class Comment(AuditModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='comments')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['work_item']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
            models.Index(fields=['tenant', 'work_item']),
            models.Index(fields=['author', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {str(self.author)} on {str(self.work_item)}"

class ActivityLog(AuditModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activity_logs')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_log')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ActivityLogActivityTypes.choices)
    description = models.TextField()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['work_item']),
            models.Index(fields=['user']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['tenant', 'work_item']),
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['work_item', 'created_at']),
        ]

    def __str__(self):
        return f"{self.activity_type} by {str(self.user)} on {str(self.work_item)}"

class Assignment(AuditModel):
    work_item = models.ForeignKey('WorkItem', on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('work_item', 'user')
        indexes = [
            models.Index(fields=['work_item']),
            models.Index(fields=['user']),
            models.Index(fields=['assigned_by']),
            models.Index(fields=['assigned_at']),
            models.Index(fields=['user', 'assigned_at']),
        ]

    def __str__(self):
        return f"{self.user} assigned to {self.work_item} by {self.assigned_by}"

