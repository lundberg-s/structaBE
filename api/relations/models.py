from django.db import models
from django.forms import ValidationError

from relations.choices import RelationObjectType, SystemRole, RelationType
from relations.utilities.validation_helpers import (
    TenantValidatorMixin,
    validate_tenant_consistency,
)
from engagements.models import WorkItem
from core.models import AuditModel, Tenant, Role
from relations.managers import (
    CustomRoleQuerySet,
    PartnerQuerySet,
    PersonQuerySet,
    OrganizationQuerySet,
    RelationQuerySet,
    RoleQuerySet,
)

# ---
# Partner Pattern: Unifies people and organizations as 'actors' in the system.
# Allows roles, relationships, and references to be generic and flexible.
# ---



# Base Partner model - can be person or organization
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




class Person(Partner):
    """
    Represents an individual (user, employee, customer, etc.).
    Inherits from Partner.
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    objects = PersonQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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





class Relation(AuditModel, TenantValidatorMixin):
    """
    Represents a relationship between two partners or workitems.
    """
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="relations"
    )

    # Source fields
    source_type = models.CharField(max_length=20, choices=RelationObjectType.choices)
    source_partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    source_workitem = models.ForeignKey(WorkItem, null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    
    # Target fields
    target_type = models.CharField(max_length=20, choices=RelationObjectType.choices)
    target_partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    target_workitem = models.ForeignKey(WorkItem, null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    objects = RelationQuerySet.as_manager()

    def clean(self):
        """Validate the relation using the validation helpers."""
        super().clean()
        
        # Validate tenant consistency
        self.validate_tenant_consistency(self.tenant, self.source_partner, self.target_partner, self.source_workitem, self.target_workitem, self.role)

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        source_str = str(self.source_partner) if self.source_partner else str(self.source_workitem)
        target_str = str(self.target_partner) if self.target_partner else str(self.target_workitem)
        return f"{source_str} → {target_str} ({self.role.label})"

    class Meta:
        constraints = [
            # Source constraints
            models.CheckConstraint(
                check=(
                    models.Q(source_partner__isnull=False, source_workitem__isnull=True) |
                    models.Q(source_partner__isnull=True, source_workitem__isnull=False)
                ),
                name="exactly_one_source_reference",
            ),
            # Target constraints
            models.CheckConstraint(
                check=(
                    models.Q(target_partner__isnull=False, target_workitem__isnull=True) |
                    models.Q(target_partner__isnull=True, target_workitem__isnull=False)
                ),
                name="exactly_one_target_reference",
            ),
        ]
