from django.db import models

class WorkItemStatusTypes(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in-progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'

class WorkItemPriorityTypes(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'

class WorkItemCategoryTypes(models.TextChoices):
    TICKET = 'ticket', 'Ticket'
    CASE = 'case', 'Case'
    JOB = 'job', 'Job'



class ActivityLogActivityTypes(models.TextChoices):
    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    STATUS_CHANGED = 'status-changed', 'Status Changed'
    PRIORITY_CHANGED = 'priority-changed', 'Priority Changed'
    DEADLINE_CHANGED = 'deadline-changed', 'Deadline Changed'
    ASSIGNED = 'assigned', 'Assigned'
    COMMENTED = 'commented', 'Commented'
    ATTACHMENT_ADDED = 'attachment-added', 'Attachment Added'