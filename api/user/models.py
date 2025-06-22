import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from user.managers import UserManager

from root.models import TimestampedModel


class User(AbstractUser, TimestampedModel):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True , primary_key=True
    )
    email = models.EmailField("email address", unique=True)
    footer_text = models.TextField(blank=True)
    external_id = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User {self.email}"