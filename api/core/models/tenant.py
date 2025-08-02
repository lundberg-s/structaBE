from django.db import models
from core.choices import WorkItemType
from .audit_model import AuditModel


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