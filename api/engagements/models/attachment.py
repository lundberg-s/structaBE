import mimetypes
from django.db import models
from core.models import Tenant, AuditModel
from relations.utilities.validation_helpers import TenantValidatorMixin


class Attachment(AuditModel, TenantValidatorMixin):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="attachments"
    )
    work_item = models.ForeignKey(
        'engagements.WorkItem', on_delete=models.CASCADE, related_name="attachments"
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