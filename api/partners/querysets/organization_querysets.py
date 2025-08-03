from django.db import models

class OrganizationQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get organizations for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_name(self, name):
        """Get organizations by name."""
        return self.filter(name__icontains=name)

    def by_organization_number(self, org_number):
        """Get organization by organization number."""
        return self.filter(organization_number=org_number)
