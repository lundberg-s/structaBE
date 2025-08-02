from django.db import models
from core.models import Tenant, AuditModel
from engagements.querysets.work_item_querysets import WorkItemQuerySet


class WorkItem(AuditModel):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="work_items"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.ForeignKey(
        'WorkItemStatus', 
        on_delete=models.PROTECT, 
        related_name='status_work_items'
    )
    category = models.ForeignKey(
        'WorkItemCategory', 
        on_delete=models.PROTECT, 
        related_name='category_work_items'
    )
    priority = models.ForeignKey(
        'WorkItemPriority', 
        on_delete=models.PROTECT, 
        related_name='priority_work_items'
    )
    deadline = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    objects = WorkItemQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["deadline"]),
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "category"]),
            models.Index(fields=["tenant", "priority"]),
            models.Index(fields=["tenant", "is_deleted"]),
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["category", "status"]),
        ]

    def get_real_instance(self):
        if hasattr(self, "ticket"):
            return self.ticket
        if hasattr(self, "case"):
            return self.case
        if hasattr(self, "job"):
            return self.job
        return self

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.status.get_display_name() if self.status else 'No Status'}"

    @property
    def assigned_to(self):
        """Get all users assigned to this work item"""
        from relations.models import Relation
        from relations.choices import RelationType
        
        # Find relations where this work item is the target and the role is "assigned_to"
        relations = Relation.objects.filter(
            target_workitem=self,
            target_type='workitem',
            role__key=RelationType.ASSIGNED_TO
        )
        
        # Get the source partners (users) from these relations
        users = []
        for relation in relations:
            if relation.source_partner and hasattr(relation.source_partner, 'person'):
                # If the source is a Person, get the associated User
                person = relation.source_partner.person
                if hasattr(person, 'user'):
                    users.append(person.user)
        
        return users 