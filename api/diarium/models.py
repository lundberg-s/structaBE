from django.db import models
import mimetypes
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from user.models import Tenant

User = get_user_model()

class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Organization(Entity):
    name = models.CharField(max_length=255)
    organization_number = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name

class Customer(Entity):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    customer_number = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Vendor(Entity):
    name = models.CharField(max_length=255)
    vendor_number = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name


class WorkItem(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='workitems')
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in-progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateTimeField(null=True, blank=True)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_workitems')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workitems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.status}"
        
class Ticket(WorkItem):
    ticket_number = models.CharField(max_length=50, unique=True)
    reported_by = models.CharField(max_length=255)
    urgency = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')])
    # entity: typically the customer or reporter
    pass

class Case(WorkItem):
    case_reference = models.CharField(max_length=100, unique=True)
    legal_area = models.CharField(max_length=100)
    court_date = models.DateField(null=True, blank=True)
    # entity: could be a person, organization, or other party involved
    pass

class Job(WorkItem):
    job_code = models.CharField(max_length=50, unique=True)
    assigned_team = models.CharField(max_length=100)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    # entity: typically the customer or client for whom the job is performed
    pass

class WorkItemEntityRole(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='workitem_entity_roles')
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('plaintiff', 'Plaintiff'),
        ('defendant', 'Defendant'),
        # Add more as needed
    ]
    workitem = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='entity_roles')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    entity = GenericForeignKey('content_type', 'object_id')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('workitem', 'content_type', 'object_id', 'role', 'tenant')

    def __str__(self):
        return f"{self.entity} as {self.role} for {self.workitem}"

class Attachment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attachments')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workitem = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='case_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and self.file.name and not self.mime_type:
            mime, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime or ''
        super().save(*args, **kwargs) 

    def __str__(self):
        return self.filename

class Comment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='comments')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workitem = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {str(self.author_id)} on {str(self.workitem_id)}"

class ActivityLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activity_logs')
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('deadline_changed', 'Deadline Changed'),
        ('assigned', 'Assigned'),
        ('commented', 'Commented'),
        ('attachment_added', 'Attachment Added'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workitem = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='activity_log')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type} by {str(self.user_id)} on {str(self.workitem_id)}"

