from django.db import models

from relations.models.partner import Partner
from relations.querysets.organization_querysets import OrganizationQuerySet


class Organization(Partner):
    """
    Represents a company or group (tenant, vendor, customer, etc.).
    Inherits from Partner.
    """

    name = models.CharField(max_length=255)
    organization_number = models.CharField(max_length=100, blank=True, null=True)

    objects = OrganizationQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["organization_number"]),
        ]

    def __str__(self):
        return self.name