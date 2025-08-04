from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager

from core.models import AuditModel, Tenant


class User(AbstractUser, AuditModel):
    """
    Represents a login account. Linked 1:1 to a Person (which is a Partner).
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User {self.email}"
