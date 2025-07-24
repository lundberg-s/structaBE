import mimetypes

from django.db import models
from django.contrib.auth import get_user_model

from core.models import Tenant, AuditModel
from engagements.managers import WorkItemQuerySet
from engagements.choices import (
    WorkItemStatusTypes,
    WorkItemPriorityTypes,
    WorkItemCategoryTypes,
    ActivityLogActivityTypes,
)
from engagements.utilities.ticket_utilities import generate_ticket_number

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
        # Use prefetched data if available
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "assignments" in self._prefetched_objects_cache
        ):
            return [
                assignment.user
                for assignment in self._prefetched_objects_cache["assignments"]
            ]
        # Fallback to database query
        return [assignment.user for assignment in self.assignments.all()]


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


class Attachment(AuditModel):
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

    def save(self, *args, **kwargs):
        if self.file and self.file.name and not self.mime_type:
            mime, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime or ""
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.filename} - {self.work_item.title}"

    class Meta:
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["work_item"]),
            models.Index(fields=["filename"]),
            models.Index(fields=["mime_type"]),
            models.Index(fields=["tenant", "work_item"]),
        ]


class Comment(AuditModel):
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
            models.Index(fields=["created_at"]),
            models.Index(fields=["tenant", "work_item"]),
        ]

    def __str__(self):
        return f"Comment by {str(self.created_by)} on {str(self.work_item)}"


class ActivityLog(AuditModel):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="activity_logs"
    )
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_log",
    )
    activity_type = models.CharField(
        max_length=20, choices=ActivityLogActivityTypes.choices
    )
    description = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["work_item"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["tenant", "work_item"]),
            models.Index(fields=["work_item", "created_at"]),
        ]

    def __str__(self):
        return f"{self.activity_type} by {str(self.created_by)} on {str(self.work_item)}"


class Assignment(AuditModel):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="assignments"
    )
    work_item = models.ForeignKey(
        "WorkItem", on_delete=models.CASCADE, related_name="assigned_to"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="assignments"
    )


    class Meta:
        unique_together = ("work_item", "user")
        indexes = [
            models.Index(fields=["work_item"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} assigned to {self.work_item} by {self.created_by}"
