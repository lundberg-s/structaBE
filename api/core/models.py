from django.db import models
import uuid


class WorkItemType(models.TextChoices):
    TICKET = 'ticket', 'Ticket'
    CASE = 'case', 'Case'
    JOB = 'job', 'Job'

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Tenant is your SaaS account, linked 1:1 with Partner
class Tenant(TimestampedModel):
    """
    Represents a SaaS account (a business using the platform).
    Linked 1:1 to a Partner (usually an Organization).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item_type = models.CharField(max_length=50, default=WorkItemType.TICKET, choices=WorkItemType.choices)
    subscription_plan = models.CharField(max_length=50, default='free')
    subscription_status = models.CharField(max_length=50, default='trial')
    billing_email = models.EmailField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)