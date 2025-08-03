from django.db import models

from core.models import AuditModel, Tenant, Role
from partners.querysets import PartnerQuerySet


class Partner(AuditModel):
    """
    Base model for any actor in the system (person or organization).
    Do not use directly; use Person or Organization.
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="partners"
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)

    objects = PartnerQuerySet.as_manager()

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        

    def __str__(self):
        # Show the name of the Organization or Person if available
        if hasattr(self, "person") and self.person:
            return str(self.person)
        if hasattr(self, "organization") and self.organization:
            return str(self.organization)
        return str(self.id)