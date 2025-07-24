from django.db import models
from django.forms import ValidationError

from relations.choices import RelationObjectType, SystemRole, RelationType
from relations.utilities.validation_helpers import (
    SingleReferenceValidatorMixin,
    TypeInstanceValidatorMixin,
    TenantValidatorMixin,
    validate_tenant_consistency,
    get_real_instance,
)
from engagements.models import WorkItem
from core.models import AuditModel, Tenant
from relations.managers import (
    CustomRoleQuerySet,
    PartnerQuerySet,
    PersonQuerySet,
    OrganizationQuerySet,
    RelationReferenceQuerySet,
    RelationQuerySet,
    RoleQuerySet,
)

# ---
# Partner Pattern: Unifies people and organizations as 'actors' in the system.
# Allows roles, relationships, and references to be generic and flexible.
# ---


class CustomRole(AuditModel):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="custom_roles"
    )
    key = models.CharField(max_length=50)
    label = models.CharField(max_length=100)

    objects = CustomRoleQuerySet.as_manager()

    class Meta:
        unique_together = ("tenant", "key")

    def __str__(self):
        return self.label


# Base Partner model - can be person or organization
class Partner(AuditModel):
    """
    Base model for any actor in the system (person or organization).
    Do not use directly; use Person or Organization.
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="partners"
    )

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

    def get_roles(self):
        """Get all roles for this partner through RelationReference."""
        from relations.models import RelationReference, Role
        refs = RelationReference.objects.filter(partner=self)
        return Role.objects.filter(target__in=refs)


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


class RelationReference(
    AuditModel, SingleReferenceValidatorMixin, TypeInstanceValidatorMixin
):
    type = models.CharField(max_length=20, choices=RelationObjectType.choices)

    partner = models.ForeignKey(
        Partner, null=True, blank=True, on_delete=models.CASCADE
    )
    workitem = models.ForeignKey(
        WorkItem, null=True, blank=True, on_delete=models.CASCADE
    )

    objects = RelationReferenceQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["partner"]),
            models.Index(fields=["workitem"]),
            models.Index(fields=["type", "partner"]),
            models.Index(fields=["type", "workitem"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(partner__isnull=False, workitem__isnull=True)
                    | models.Q(partner__isnull=True, workitem__isnull=False)
                ),
                name="exactly_one_reference",
            )
        ]

    def __str__(self):
        if self.partner:
            return str(self.partner)
        if self.workitem:
            return str(self.workitem)
        return str(self.id)


class Relation(AuditModel, TenantValidatorMixin):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="relations"
    )

    source = models.ForeignKey(
        "RelationReference", on_delete=models.CASCADE, related_name="relation_sources"
    )
    target = models.ForeignKey(
        "RelationReference", on_delete=models.CASCADE, related_name="relation_targets"
    )

    relation_type = models.CharField(
        max_length=50, choices=RelationType.choices, null=True, blank=True
    )

    objects = RelationQuerySet.as_manager()



    def __str__(self):
        return f"{self.source} → {self.target} ({self.relation_type})"

    class Meta:
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["relation_type"]),
            models.Index(fields=["source"]),
            models.Index(fields=["target"]),
            models.Index(fields=["tenant", "relation_type"]),
            models.Index(fields=["source", "target"]),
            models.Index(fields=["tenant", "source"]),
            models.Index(fields=["tenant", "target"]),
        ]


# Role to assign multiple roles to one Partner if needed
class Role(AuditModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="roles")
    target = models.ForeignKey(RelationReference, on_delete=models.CASCADE)

    system_role = models.CharField(
        max_length=50, choices=SystemRole.choices, null=True, blank=True
    )
    custom_role = models.ForeignKey(
        CustomRole, null=True, blank=True, on_delete=models.PROTECT
    )

    objects = RoleQuerySet.as_manager()



    def __str__(self):
        role = (
            self.get_system_role_display()
            if self.system_role
            else self.custom_role.label
        )
        return f"{self.target} as {role}"

    def get_role_type_display(self):
        return self.get_system_role_display() if self.system_role else self.custom_role.label
    
    class Meta:
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["target"]),
            models.Index(fields=["system_role"]),
            models.Index(fields=["custom_role"]),
            models.Index(fields=["tenant", "system_role"]),
            models.Index(fields=["tenant", "custom_role"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "target", "system_role"],
                condition=models.Q(system_role__isnull=False),
                name="unique_system_role_per_target",
            ),
            models.UniqueConstraint(
                fields=["tenant", "target", "custom_role"],
                condition=models.Q(custom_role__isnull=False),
                name="unique_custom_role_per_target",
            ),
        ]
