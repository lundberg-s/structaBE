from django.db import models


class RelationQuerySet(models.QuerySet):
    def by_tenant(self, tenant):
        """Get relations for a specific tenant."""
        return self.filter(tenant=tenant)

    def by_type(self, relation_type):
        """Get relations by type."""
        return self.filter(relation_type=relation_type)

    def by_partner(self, partner):
        """Get all relations involving a specific partner."""
        return self.filter(
            models.Q(source_partner=partner) | models.Q(target_partner=partner)
        )

    def by_work_item(self, work_item):
        """Get all relations involving a specific work item."""
        return self.filter(
            models.Q(source_workitem=work_item) | models.Q(target_workitem=work_item)
        )