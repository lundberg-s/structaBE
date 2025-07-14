import mimetypes
import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from core.models import Tenant, TimestampedModel

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

class WorkItem(TimestampedModel):
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

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.status}"
        
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

class WorkItemPartnerRole(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='work_item_partner_roles')
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='partner_roles')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    partner = GenericForeignKey('content_type', 'object_id')
    role = models.CharField(max_length=20, choices=WorkItemPartnerRoleTypes.choices)

    class Meta:
        unique_together = ('work_item', 'content_type', 'object_id', 'role', 'tenant')

    def __str__(self):
        return f"{self.partner} as {self.role} for {self.work_item}"

class Attachment(TimestampedModel):
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
        return self.filename

class Comment(TimestampedModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='comments')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {str(self.author)} on {str(self.work_item)}"

class ActivityLog(TimestampedModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activity_logs')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_log')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ActivityLogActivityTypes.choices)
    description = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type} by {str(self.user)} on {str(self.work_item)}"

class Assignment(TimestampedModel):
    work_item = models.ForeignKey('WorkItem', on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('work_item', 'user')

    def __str__(self):
        return f"{self.user} assigned to {self.work_item} by {self.assigned_by}"

