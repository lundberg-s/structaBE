import mimetypes

from django.db import models
from django.contrib.auth import get_user_model

from core.models import Tenant, AuditModel
from engagements.managers import WorkItemQuerySet
from engagements.choices import (
    WorkItemStatusTypes,
    WorkItemPriorityTypes,
    WorkItemCategoryTypes,
)
from engagements.utilities.ticket_utilities import generate_ticket_number
from relations.utilities.validation_helpers import TenantValidatorMixin, validate_tenant_consistency

User = get_user_model()


class WorkItem(AuditModel):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="work_items"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=WorkItemStatusTypes.choices,
        default=WorkItemStatusTypes.OPEN,
    )
    category = models.CharField(max_length=100, choices=WorkItemCategoryTypes.choices)
    priority = models.CharField(
        max_length=20,
        choices=WorkItemPriorityTypes.choices,
        default=WorkItemPriorityTypes.MEDIUM,
    )
    deadline = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    objects = WorkItemQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["deadline"]),
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "category"]),
            models.Index(fields=["tenant", "priority"]),
            models.Index(fields=["tenant", "is_deleted"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["category", "status"]),
        ]

    def get_real_instance(self):
        if hasattr(self, "ticket"):
            return self.ticket
        if hasattr(self, "case"):
            return self.case
        if hasattr(self, "job"):
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
        from relations.models import Relation
        from relations.choices import RelationType
        
        # Find relations where this work item is the target and the role is "assigned_to"
        relations = Relation.objects.filter(
            target_workitem=self,
            target_type='workitem',
            role__key=RelationType.ASSIGNED_TO
        )
        
        # Get the source partners (users) from these relations
        users = []
        for relation in relations:
            if relation.source_partner and hasattr(relation.source_partner, 'person'):
                # If the source is a Person, get the associated User
                person = relation.source_partner.person
                if hasattr(person, 'user'):
                    users.append(person.user)
        
        return users


class Ticket(WorkItem):
    # Auto-generated 7-digit unique ticket number
    ticket_number = models.CharField(max_length=50, null=True, blank=True, unique=True, editable=False)
    urgency = models.CharField(
        max_length=20,
        choices=WorkItemPriorityTypes.choices,
        default=WorkItemPriorityTypes.MEDIUM,
    )
    # entity: typically the customer or reporter
    
    def save(self, *args, **kwargs):
        # Auto-generate ticket number if not provided
        if not self.ticket_number:
            self.ticket_number = generate_ticket_number(self.tenant)
        super().save(*args, **kwargs)
    
    class Meta:
        indexes = [
            models.Index(fields=["ticket_number"]),
        ]


class Case(WorkItem):
    case_reference = models.CharField(max_length=100, unique=True)
    legal_area = models.CharField(max_length=100)
    court_date = models.DateField(null=True, blank=True)
    # entity: could be a person, organization, or other partner involved
    pass


class Job(WorkItem):
    job_code = models.CharField(max_length=50, unique=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    # entity: typically the customer or client for whom the job is performed
    pass


class Attachment(AuditModel, TenantValidatorMixin):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="attachments"
    )
    work_item = models.ForeignKey(
        WorkItem, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="case_attachments/")
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["work_item"]),
            models.Index(fields=["filename"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["tenant", "work_item"]),
            models.Index(fields=["tenant", "created_by"]),
        ]

    def clean(self):
        """Validate the attachment using the validation helpers."""
        super().clean()
        
        # Validate tenant consistency
        self.validate_tenant_consistency(self.tenant, self.work_item)

    def save(self, *args, **kwargs):
        """Override save to run validation and handle mime type detection."""
        self.clean()
        
        # Handle mime type detection
        if self.file and self.file.name and not self.mime_type:
            mime, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime or ""
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.filename} attached to {self.work_item.title}"


class Comment(AuditModel, TenantValidatorMixin):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="comments"
    )
    work_item = models.ForeignKey(
        WorkItem, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["work_item"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["tenant", "work_item"]),
            models.Index(fields=["tenant", "created_by"]),
        ]

    def clean(self):
        """Validate the comment using the validation helpers."""
        super().clean()
        
        # Validate tenant consistency
        self.validate_tenant_consistency(self.tenant, self.work_item)

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.created_by.username} on {self.work_item.title}"

