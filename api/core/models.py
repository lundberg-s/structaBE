from django.db import models
from django.core.exceptions import ValidationError
import uuid

from core.choices import WorkItemType
from core.enums.system_role_enums import SystemRole
from core.managers.role_managers import RoleQuerySet

class AuditModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_created")
    updated_by = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Tenant is your SaaS account, linked 1:1 with Partner
class Tenant(AuditModel):
    """
    Represents a SaaS account (a business using the platform).
    Linked 1:1 to a Partner (usually an Organization).
    """

    work_item_type = models.CharField(
        max_length=50, default=WorkItemType.TICKET, choices=WorkItemType.choices
    )
    subscription_plan = models.CharField(max_length=50, default="free")
    subscription_status = models.CharField(max_length=50, default="trial")
    billing_email = models.EmailField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)



class Role(AuditModel):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles"
    )  # Null for system roles

    key = models.SlugField(max_length=50)
    label = models.CharField(max_length=100)
    is_system = models.BooleanField(default=False)

    objects = RoleQuerySet.as_manager()

    def clean(self):
        # Validate system roles have valid keys
        if self.is_system and self.key not in [role.value for role in SystemRole]:
            raise ValidationError(f"{self.key} is not a valid system role key")

    def save(self, *args, **kwargs):
        self.full_clean()  # call clean before saving
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["key"],
                condition=models.Q(is_system=True),
                name="unique_system_role_key"
            ),
            models.UniqueConstraint(
                fields=["tenant", "key"],
                condition=models.Q(is_system=False),
                name="unique_tenant_role_key"
            ),
        ]

    def __str__(self):
        return self.label