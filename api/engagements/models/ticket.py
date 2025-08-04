from django.db import models
from engagements.choices.work_item_choices import WorkItemPriorityTypes
from engagements.utilities.ticket_utilities import generate_ticket_number
from .work_item import WorkItem


class Ticket(WorkItem):
    # Auto-generated 7-digit unique ticket number
    ticket_number = models.CharField(max_length=50, null=True, blank=True, unique=True, editable=False)
    # entity: typically the customer or reporter
    
    def save(self, *args, **kwargs):
        # Auto-generate ticket number if not provided
        if not self.ticket_number:
            self.ticket_number = generate_ticket_number(self.tenant)
        super().save(*args, **kwargs)
    
    class Meta:
        indexes = [
            models.Index(fields=["ticket_number"]),
        ] 