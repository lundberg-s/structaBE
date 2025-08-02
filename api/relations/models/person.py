from django.db import models

from relations.models.partner import Partner
from relations.querysets.person_querysets import PersonQuerySet


class Person(Partner):
    """
    Represents an individual (user, employee, customer, etc.).
    Inherits from Partner.
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    objects = PersonQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
