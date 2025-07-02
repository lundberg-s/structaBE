import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from user.managers import UserManager

from root.models import TimestampedModel


class Tenant(models.Model):
    """Represents a SaaS tenant (a business using the platform)."""
    WORKITEM_TYPE_CHOICES = [
        ('ticket', 'Ticket'),
        ('case', 'Case'),
        ('job', 'Job'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subscription_plan = models.CharField(max_length=50, default='free')
    subscription_status = models.CharField(max_length=50, default='trial')
    billing_email = models.EmailField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    payment_customer_id = models.CharField(max_length=100, blank=True, null=True)
    trial_start = models.DateTimeField(blank=True, null=True)
    trial_end = models.DateTimeField(blank=True, null=True)
    workitem_type = models.CharField(max_length=20, choices=WORKITEM_TYPE_CHOICES, default='ticket')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class User(AbstractUser, TimestampedModel):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True , primary_key=True
    )
    email = models.EmailField("email address", unique=True)
    footer_text = models.TextField(blank=True)
    external_id = models.TextField(blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User {self.email} ({self.tenant.name})"