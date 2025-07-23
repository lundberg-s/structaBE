from django.db import models
import uuid

from core.choices import WorkItemType


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
