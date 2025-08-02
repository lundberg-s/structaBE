from django.db import models


class WorkItemType(models.TextChoices):
    TICKET = "ticket", "Ticket"
    CASE = "case", "Case"
    JOB = "job", "Job"
