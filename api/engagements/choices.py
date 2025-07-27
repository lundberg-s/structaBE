from django.db import models


class WorkItemStatusTypes(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    ON_HOLD = "on_hold", "On Hold"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class WorkItemPriorityTypes(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class WorkItemCategoryTypes(models.TextChoices):
    BUG = "bug", "Bug"
    FEATURE = "feature", "Feature"
    TASK = "task", "Task"
    IMPROVEMENT = "improvement", "Improvement"
    SUPPORT = "support", "Support"