from django.db import models

class RoleQuerySet(models.QuerySet):
    def system(self):
        """Return system roles only (not tied to any tenant)."""
        return self.filter(is_system=True)

    def tenant(self, tenant):
        """Return roles specific to a given tenant."""
        return self.filter(is_system=False, tenant=tenant)

    def for_tenant_inclusive(self, tenant):
        """
        Return both system and tenant roles available to a tenant.
        Useful when showing all assignable roles.
        """
        return self.filter(
            models.Q(is_system=True) |
            models.Q(tenant=tenant)
        )

    def by_key(self, key):
        """Fetch a role by its system key (e.g. 'admin', 'user', etc.)."""
        return self.filter(system_role=key, is_system=True).first()

    def assignable(self, tenant):
        """
        Returns all roles that could be assigned within a given tenant scope.
        (System + Tenant-specific).
        """
        return self.for_tenant_inclusive(tenant)
