import uuid

from django.db import models
from django.forms import ValidationError

from relations.choices import RelationObjectType, SystemRole, RelationType
from relations.utilities.validation_helpers import (
    SingleReferenceValidatorMixin, 
    TypeInstanceValidatorMixin,
    TenantValidatorMixin,
    validate_tenant_consistency,
    get_real_instance
)
from engagements.models import WorkItem
from core.models import AuditModel, Tenant

# ---
# Partner Pattern: Unifies people and organizations as 'actors' in the system.
# Allows roles, relationships, and references to be generic and flexible.
# ---

class PartnerManager(models.Manager):
    """Manager for SAP-style partner queries"""
    
    def customers(self, tenant):
        """Get all customers for a tenant with optimized queries."""
        return self.filter(tenant=tenant).select_related('person', 'organization')
    
    def vendors(self, tenant):
        """Get all vendors for a tenant with optimized queries."""
        return self.filter(tenant=tenant).select_related('person', 'organization')

    def by_work_item(self, work_item):
        """Get all partners involved in a work item with optimized queries."""
        from relations.models import RelationReference
        refs = RelationReference.objects.filter(workitem=work_item).select_related('partner__person', 'partner__organization')
        return self.filter(id__in=[ref.partner.id for ref in refs])
    
    def with_relations(self, tenant):
        """Get partners with their relations preloaded for better performance."""
        return self.filter(tenant=tenant).prefetch_related(
            'relation_sources__target__partner',
            'relation_targets__source__partner'
        )

    def with_roles(self, tenant):
        """Get partners with their roles preloaded for better performance."""
        return self.filter(tenant=tenant).prefetch_related(
            'relation_sources__roles',
            'relation_targets__roles'
        )

    def with_work_items(self, tenant):
        """Get partners with their work items preloaded for better performance."""
        return self.filter(tenant=tenant).prefetch_related(
            'relation_sources__workitem',
            'relation_targets__workitem'
        )


class CustomRole(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='custom_roles')
    key = models.CharField(max_length=50)
    label = models.CharField(max_length=100)

    class Meta:
        unique_together = ('tenant', 'key')

    def __str__(self):
        return self.label


# Base Partner model - can be person or organization
class Partner(AuditModel):
    """
    Base model for any actor in the system (person or organization).
    Do not use directly; use Person or Organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='partners')

    objects = PartnerManager()

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def get_real_instance(self):
        """Get the actual Person or Organization instance."""
        if hasattr(self, 'person'):
            return self.person
        if hasattr(self, 'organization'):
            return self.organization
        return self

    def get_roles(self):
        """Get all roles for this partner through RelationReference."""
        from relations.models import RelationReference, Role
        refs = RelationReference.objects.filter(partner=self)
        return Role.objects.filter(target__in=refs)

    def get_relations(self):
        """Get all relations where this partner is involved."""
        from relations.models import RelationReference, Relation
        refs = RelationReference.objects.filter(partner=self)
        return Relation.objects.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        )

    def get_work_items(self):
        """Get all work items this partner is involved in through relations"""
        from engagements.models import WorkItem
        return WorkItem.objects.filter(
            relation_targets__source__partner=self
        ).distinct()

    def get_contact_info(self):
        """Get contact information for this partner."""
        real_instance = self.get_real_instance()
        if hasattr(real_instance, 'email'):
            return {
                'email': real_instance.email,
                'phone': getattr(real_instance, 'phone', None),
            }
        return {}

    def __str__(self):
        # Show the name of the Organization or Person if available
        real_instance = self.get_real_instance()
        if hasattr(real_instance, 'name'):
            return real_instance.name
        if hasattr(real_instance, 'first_name') and hasattr(real_instance, 'last_name'):
            return f"{real_instance.first_name} {real_instance.last_name}"
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

    class Meta:
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
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

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['organization_number']),
        ]

    def __str__(self):
        return self.name
    

class RelationReference(models.Model, SingleReferenceValidatorMixin, TypeInstanceValidatorMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=RelationObjectType.choices)

    partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.CASCADE)
    workitem = models.ForeignKey(WorkItem, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['partner']),
            models.Index(fields=['workitem']),
            models.Index(fields=['type', 'partner']),
            models.Index(fields=['type', 'workitem']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(partner__isnull=False, workitem__isnull=True) |
                    models.Q(partner__isnull=True, workitem__isnull=False)
                ),
                name='exactly_one_reference'
            )
        ]

    def get_object(self):
        if self.partner:
            return get_real_instance(self.partner)
        if self.workitem:
            return get_real_instance(self.workitem)

    def validate_tenant(self, tenant):
        obj = self.get_object()
        validate_tenant_consistency(tenant, obj)

    def clean(self):
        super().clean()
        
        # Use mixin to validate exactly one reference is set
        self.validate_single_reference('partner', 'workitem')

        # Validate type matches FK subclass using mixin
        if self.partner:
            real_instance = get_real_instance(self.partner)
            type_mapping = {
                Person: 'person',
                Organization: 'organization'
            }
            self.validate_type_matches_instance(real_instance, self.type, type_mapping)

        if self.workitem and self.type != 'workitem':
            raise ValidationError("Type must be 'workitem' if workitem FK is set.")

    def __str__(self):
        return str(self.get_object())


class RelationQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related(
            'source__partner__person',
            'source__partner__organization',
            'source__workitem',
            'target__partner__person',
            'target__partner__organization',
            'target__workitem'
        )

    def by_tenant(self, tenant):
        """Get relations for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_type(self, relation_type):
        """Get relations by type with optimized queries."""
        return self.filter(relation_type=relation_type).with_details()

    def by_partner(self, partner):
        """Get all relations involving a specific partner."""
        from relations.models import RelationReference
        refs = RelationReference.objects.filter(partner=partner)
        return self.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        ).with_details()

    def by_work_item(self, work_item):
        """Get all relations involving a specific work item."""
        from relations.models import RelationReference
        refs = RelationReference.objects.filter(workitem=work_item)
        return self.filter(
            models.Q(source__in=refs) | models.Q(target__in=refs)
        ).with_details()


class Relation(AuditModel, TenantValidatorMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='relations')

    source = models.ForeignKey('RelationReference', on_delete=models.CASCADE, related_name='relation_sources')
    target = models.ForeignKey('RelationReference', on_delete=models.CASCADE, related_name='relation_targets')

    relation_type = models.CharField(max_length=50, choices=RelationType.choices, null=True, blank=True)

    objects = RelationQuerySet.as_manager()

    def clean(self):
        # Use mixin to validate tenant consistency
        self.validate_tenant_consistency(self.tenant, self.source.get_object(), self.target.get_object())
        
        if self.source == self.target:
            raise ValidationError("Source and target cannot be the same.")

    def __str__(self):
        return f"{self.source} → {self.target} ({self.relation_type})"

    class Meta:
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['relation_type']),
            models.Index(fields=['source']),
            models.Index(fields=['target']),
            models.Index(fields=['tenant', 'relation_type']),
            models.Index(fields=['source', 'target']),
            models.Index(fields=['tenant', 'source']),
            models.Index(fields=['tenant', 'target']),
        ]

class RoleQuerySet(models.QuerySet):
    def with_details(self):
        """Preload all related objects for better performance."""
        return self.select_related(
            'target__partner__person',
            'target__partner__organization',
            'target__workitem',
            'custom_role'
        )

    def by_tenant(self, tenant):
        """Get roles for a specific tenant with optimized queries."""
        return self.filter(tenant=tenant).with_details()

    def by_system_role(self, system_role):
        """Get roles by system role with optimized queries."""
        return self.filter(system_role=system_role).with_details()

    def by_custom_role(self, custom_role):
        """Get roles by custom role with optimized queries."""
        return self.filter(custom_role=custom_role).with_details()

    def by_partner(self, partner):
        """Get all roles for a specific partner."""
        from relations.models import RelationReference
        refs = RelationReference.objects.filter(partner=partner)
        return self.filter(target__in=refs).with_details()

    def by_work_item(self, work_item):
        """Get all roles for a specific work item."""
        from relations.models import RelationReference
        refs = RelationReference.objects.filter(workitem=work_item)
        return self.filter(target__in=refs).with_details()


# Role to assign multiple roles to one Partner if needed
class Role(AuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    target = models.ForeignKey(RelationReference, on_delete=models.CASCADE)

    system_role = models.CharField(max_length=50, choices=SystemRole.choices, null=True, blank=True)
    custom_role = models.ForeignKey(CustomRole, null=True, blank=True, on_delete=models.PROTECT)

    objects = RoleQuerySet.as_manager()

    def clean(self):
        if not self.system_role and not self.custom_role:
            raise ValidationError("Either system_role or custom_role must be set.")
        if self.system_role and self.custom_role:
            raise ValidationError("Only one of system_role or custom_role can be set.")

    def __str__(self):
        role = self.get_system_role_display() if self.system_role else self.custom_role.label
        return f"{self.target} as {role}"

    class Meta:
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['target']),
            models.Index(fields=['system_role']),
            models.Index(fields=['custom_role']),
            models.Index(fields=['tenant', 'system_role']),
            models.Index(fields=['tenant', 'custom_role']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'target', 'system_role'],
                condition=models.Q(system_role__isnull=False),
                name='unique_system_role_per_target'
            ),
            models.UniqueConstraint(
                fields=['tenant', 'target', 'custom_role'],
                condition=models.Q(custom_role__isnull=False),
                name='unique_custom_role_per_target'
            )
        ]
