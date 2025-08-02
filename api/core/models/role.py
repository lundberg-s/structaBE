from django.db import models
from django.core.exceptions import ValidationError
from core.enums.system_role_enums import SystemRole
from core.managers.role_managers import RoleQuerySet
from .audit_model import AuditModel


class Role(AuditModel):
    tenant = models.ForeignKey(
        "Tenant",
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