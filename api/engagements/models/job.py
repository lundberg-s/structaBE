from django.db import models
from .work_item import WorkItem


class Job(WorkItem):
    job_code = models.CharField(max_length=50, unique=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2)
    # entity: typically the customer or client for whom the job is performed
    pass 