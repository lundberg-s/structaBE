from django.db import models

class PersonQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get persons for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_name(self, first_name=None, last_name=None):
        """Get persons by name."""
        queryset = self
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset

    def by_email(self, email):
        """Get person by email."""
        return self.filter(email=email)
