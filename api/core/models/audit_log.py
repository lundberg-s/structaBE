from django.db import models
from django.core.exceptions import ValidationError
from .audit_model import AuditModel


class AuditLog(AuditModel):
    """
    Professional SAP-style audit trail for compliance and forensic purposes.
    Immutable, tamper-proof audit records that survive data deletion.
    """
    tenant = models.ForeignKey("Tenant", on_delete=models.SET_NULL, related_name="audit_logs", null=True, blank=True)
    
    # Entity identification (survives deletion)
    entity_type = models.CharField(max_length=50, choices=[
        ('workitem', 'Work Item'),
        ('ticket', 'Ticket'),
        ('case', 'Case'),
        ('job', 'Job'),
        ('person', 'Person'),
        ('organization', 'Organization'),
        ('relation', 'Relation'),
        ('comment', 'Comment'),
        ('attachment', 'Attachment'),
        ('assignment', 'Assignment'),
        ('role', 'Role'),
        ('user', 'User'),
        ('tenant', 'Tenant'),
    ])
    entity_id = models.UUIDField()
    entity_name = models.CharField(max_length=255)  # Snapshot of entity name
    
    # Activity tracking
    activity_type = models.CharField(max_length=50, choices=[
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('assigned', 'Assigned'),
        ('commented', 'Commented'),
        ('viewed', 'Viewed'),
        ('exported', 'Exported'),
        ('imported', 'Imported'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
        ('restored', 'Restored'),
    ])
    
    # Professional audit fields
    description = models.TextField()
    change_summary = models.JSONField(null=True, blank=True)  # Structured change data
    old_values = models.JSONField(null=True, blank=True)  # Previous state
    new_values = models.JSONField(null=True, blank=True)  # New state
    
    # Forensic tracking
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    business_process = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Compliance tracking
    compliance_category = models.CharField(max_length=50, choices=[
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('security', 'Security'),
        ('privacy', 'Privacy'),
        ('regulatory', 'Regulatory'),
    ], null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='low')
    
    # Immutability protection
    is_immutable = models.BooleanField(default=True)  # Prevent tampering
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(entity_type__in=[
                    'workitem', 'ticket', 'case', 'job', 'person', 'organization', 
                    'relation', 'comment', 'attachment', 'assignment', 'role',
                    'user', 'tenant'
                ]),
                name='valid_entity_type'
            )
        ]
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['compliance_category']),
            models.Index(fields=['risk_level']),
            # Composite indexes for performance
            models.Index(fields=['tenant', 'entity_type']),
            models.Index(fields=['tenant', 'entity_type', 'entity_id']),
            models.Index(fields=['tenant', 'activity_type']),
            models.Index(fields=['tenant', 'created_by']),
            models.Index(fields=['entity_type', 'activity_type']),
        ]

    def __str__(self):
        return f"{self.activity_type} on {self.entity_type} '{self.entity_name}' by {self.created_by}"
    
    def save(self, *args, **kwargs):
        """Ensure audit logs are immutable once created."""
        # Only prevent updates to existing records, not creation of new ones
        if self.pk and not kwargs.get('force_insert', False) and self.is_immutable:
            # Prevent updates to existing audit logs
            raise ValidationError("Audit logs are immutable and cannot be modified.")
        super().save(*args, **kwargs) 