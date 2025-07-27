from django.db import models
from django.utils import timezone
from datetime import timedelta

class WorkItemQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def with_deleted(self):
        return self.all()

    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

    def for_status(self, status):
        return self.filter(status=status)

    def for_category(self, category):
        return self.filter(category=category)

    def for_priority(self, priority):
        return self.filter(priority=priority)

    def overdue(self):
        return self.filter(
            deadline__lt=timezone.now(), status__in=["open", "in-progress"]
        )

    def due_within(self, days=7):
        future_date = timezone.now() + timedelta(days=days)
        return self.filter(
            deadline__lte=future_date,
            deadline__gt=timezone.now(),
            status__in=["open", "in-progress"],
        )
