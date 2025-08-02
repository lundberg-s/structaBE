from django.db import models

class PartnerQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get partners for a specific tenant."""
        return self.filter(tenant=tenant)