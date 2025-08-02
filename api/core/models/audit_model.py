import uuid
from django.db import models


class AuditModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_created")
    updated_by = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 