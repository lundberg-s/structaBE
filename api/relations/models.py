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
    
    Design Convention: Always Source → Role → Target
    - The role reflects the SOURCE's perspective
    - Source is the entity that "owns" or "initiates" the relationship
    - Target is the entity that the relationship is "to"
    
    Examples:
    - Person - "assigned to" - WorkItem (Person's perspective: "I am assigned to this work item")
    - Person → "Employee Of" → Organization (Person's perspective: "I am an employee of this org")
    - Person → "Contact For" → Organization (Person's perspective: "I am a contact for this org")
    - Person → "Assigned To" → WorkItem (Person's perspective: "I am assigned to this work item")
    - WorkItem → "Depends On" → WorkItem (WorkItem's perspective: "I depend on this other work item")
    - Organization → "Parent Of" → Organization (Organization's perspective: "I am the parent of this org")
    
    This eliminates ambiguity by anchoring on who initiates/owns the role.
    """
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="relations"
    )

    # Source fields (the entity that "owns" the relationship)
    source_type = models.CharField(max_length=20, choices=RelationObjectType.choices)
    source_partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    source_workitem = models.ForeignKey(WorkItem, null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    
    # Target fields (the entity the relationship is "to")
    target_type = models.CharField(max_length=20, choices=RelationObjectType.choices)
    target_partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    target_workitem = models.ForeignKey(WorkItem, null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    
    # Role (describes the relationship FROM source's perspective TO target)
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

    def get_source(self):
        """Get the source entity (the one that 'owns' the relationship)."""
        if self.source_type == 'partner':
            return self.source_partner
        elif self.source_type == 'workitem':
            return self.source_workitem
        return None
    
    def get_target(self):
        """Get the target entity (the one the relationship is 'to')."""
        if self.target_type == 'partner':
            return self.target_partner
        elif self.target_type == 'workitem':
            return self.target_workitem
        return None
    
    def get_relationship_description(self):
        """
        Get a human-readable description of the relationship from source's perspective.
        
        Examples:
        - "Sandi Lundberg is Employee Of My Company"
        - "Bug #123 Depends On Feature #456"
        """
        source = self.get_source()
        target = self.get_target()
        if source and target:
            return f"{source} is {self.role.label} {target}"
        return f"{source} → {self.role.label} → {target}"

    def __str__(self):
        """String representation following Source → Role → Target convention."""
        source = self.get_source()
        target = self.get_target()
        return f"{source} → {self.role.label} → {target}"

    class Meta:
        constraints = [
            # existing check constraints
            models.CheckConstraint(
                check=(
                    models.Q(source_partner__isnull=False, source_workitem__isnull=True) |
                    models.Q(source_partner__isnull=True, source_workitem__isnull=False)
                ),
                name="exactly_one_source_reference",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(target_partner__isnull=False, target_workitem__isnull=True) |
                    models.Q(target_partner__isnull=True, target_workitem__isnull=False)
                ),
                name="exactly_one_target_reference",
            ),
            # Unique constraint to avoid duplicate relations
            models.UniqueConstraint(
                fields=[
                    'tenant',
                    'source_type',
                    'source_partner',
                    'source_workitem',
                    'target_type',
                    'target_partner',
                    'target_workitem',
                    'role',
                ],
                name='unique_relation_per_source_target_role'
            ),
        ]

        indexes = [
            # Indexes on FKs for faster lookups
            models.Index(fields=['tenant', 'source_partner']),
            models.Index(fields=['tenant', 'source_workitem']),
            models.Index(fields=['tenant', 'target_partner']),
            models.Index(fields=['tenant', 'target_workitem']),
        ]



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