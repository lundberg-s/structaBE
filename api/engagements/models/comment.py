from django.db import models
from core.models import Tenant, AuditModel
from relations.utilities.validation_helpers import TenantValidatorMixin


class Comment(AuditModel, TenantValidatorMixin):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="comments"
    )
    work_item = models.ForeignKey(
        'engagements.WorkItem', on_delete=models.CASCADE, related_name="comments"
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
        return f"Comment by {self.created_by} on {self.work_item.title}" 