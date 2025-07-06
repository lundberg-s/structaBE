import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from user.managers import UserManager

from root.models import TimestampedModel

# ---
# Partner Pattern: Unifies people and organizations as 'actors' in the system.
# Allows roles, relationships, and references to be generic and flexible.
# ---

class WorkItemType(models.TextChoices):
    TICKET = 'ticket', 'Ticket'
    CASE = 'case', 'Case'
    JOB = 'job', 'Job'


class PartnerRoleTypes(models.TextChoices):
    # Super user roles
    SUPER_USER = 'super_user', 'Super User'
    ADMIN = 'admin', 'Admin'
    # User roles
    USER = 'user', 'User'
    READ_ONLY = 'readonly', 'Read Only'
    # Tenant roles
    TENANT = 'tenant', 'Tenant'
    TENANT_OWNER = 'tenant_owner', 'Tenant Owner'
    TENANT_MANAGER = 'tenant_manager', 'Tenant Manager'
    TENANT_ADMIN = 'tenant_admin', 'Tenant Admin'
    TENANT_BILLING = 'tenant_billing', 'Tenant Billing'
    TENANT_EMPLOYEE = 'tenant_employee', 'Tenant Employee'
    TENANT_READ_ONLY = 'tenant_readonly', 'Tenant Read Only'
    # Partner roles
    CONTACT_INFO = 'contact_info', 'Contact Info'

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


# Base Partner model - can be person or organization
class Partner(TimestampedModel):
    """
    Base model for any actor in the system (person or organization).
    Do not use directly; use Person or Organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='partners')

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Parties"

    def __str__(self):
        # Show the name of the Organization or Person if available
        if hasattr(self, 'organization') and self.organization.name:
            return self.organization.name
        if hasattr(self, 'person') and self.person.first_name:
            return f"{self.person.first_name} {self.person.last_name}"
        return f"Partner {self.id}"

class Person(Partner):
    """
    Represents an individual (user, employee, customer, etc.).
    Inherits from Partner.
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Organization(Partner):
    """
    Represents a company or group (tenant, vendor, customer, etc.).
    Inherits from Partner.
    """
    name = models.CharField(max_length=255)
    organization_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

# Role to assign multiple roles to one Partner if needed
class Role(TimestampedModel):
    """
    Assigns a business role (admin, member, customer, etc.) to any Partner (person or org).
    Users can have multiple roles per tenant.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='roles')
    role_type = models.CharField(max_length=50, choices=PartnerRoleTypes.choices)

    def __str__(self):
        return f"{self.partner} as {self.role_type}"


class User(AbstractUser, TimestampedModel):
    """
    Represents a login account. Linked 1:1 to a Person (which is a Partner).
    """
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True , primary_key=True
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    email = models.EmailField("email address", unique=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User {self.email} ({self.partner})" if self.partner else f"User {self.email}"