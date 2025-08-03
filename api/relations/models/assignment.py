from django.db import models

from relations.utilities.validation_helpers import TenantValidatorMixin
from relations.models import Relation
from core.models import AuditModel, Tenant


class Assignment(AuditModel, TenantValidatorMixin):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="assignments"
    )
    relation = models.ForeignKey(Relation, on_delete=models.CASCADE, related_name="assignments")

    class Meta:
        unique_together = ("relation",)
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["relation"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["tenant", "relation"]),
        ]

    def clean(self):
        """Validate the assignment using the validation helpers."""
        super().clean()
        
        # Validate tenant consistency
        self.validate_tenant_consistency(self.tenant, self.relation)

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assignment: {self.relation}"