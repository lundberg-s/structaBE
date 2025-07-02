import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from user.managers import UserManager

from root.models import TimestampedModel

# ---
# Party Pattern: Unifies people and organizations as 'actors' in the system.
# Allows roles, relationships, and references to be generic and flexible.
# ---

# Base Party model - can be person or organization
class Party(TimestampedModel):
    """
    Base model for any actor in the system (person or organization).
    Do not use directly; use Person or Organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"

    def __str__(self):
        # Show the name of the Organization or Person if available
        if hasattr(self, 'organization') and self.organization.name:
            return self.organization.name
        if hasattr(self, 'person') and self.person.first_name:
            return f"{self.person.first_name} {self.person.last_name}"
        return f"Party {self.id}"

class Person(Party):
    """
    Represents an individual (user, employee, customer, etc.).
    Inherits from Party.
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Organization(Party):
    """
    Represents a company or group (tenant, vendor, customer, etc.).
    Inherits from Party.
    """
    name = models.CharField(max_length=255)
    organization_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

# Role to assign multiple roles to one Party if needed
class Role(TimestampedModel):
    """
    Assigns a business role (admin, member, customer, etc.) to any Party (person or org).
    Users can have multiple roles per tenant.
    """
    ROLE_CHOICES = [
        ('super_user', 'Super User'),
        ('admin', 'Admin'),
        ('tenant_owner', 'Tenant Owner'),
        ('tenant_admin', 'Tenant Admin'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('billing', 'Billing'),
        ('readonly', 'Read Only'),
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('employee', 'Employee'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='roles')
    role_type = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.party} as {self.role_type}"

# Tenant is your SaaS account, linked 1:1 with Party
class Tenant(TimestampedModel):
    """
    Represents a SaaS account (a business using the platform).
    Linked 1:1 to a Party (usually an Organization).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name='tenant_obj')
    subscription_plan = models.CharField(max_length=50, default='free')
    subscription_status = models.CharField(max_length=50, default='trial')
    billing_email = models.EmailField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.party)

class User(AbstractUser, TimestampedModel):
    """
    Represents a login account. Linked 1:1 to a Person (which is a Party).
    """
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True , primary_key=True
    )
    email = models.EmailField("email address", unique=True)
    footer_text = models.TextField(blank=True)
    external_id = models.TextField(blank=True, null=True)
    party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User {self.email} ({self.party})" if self.party else f"User {self.email}"