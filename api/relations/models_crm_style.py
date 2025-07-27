"""
CRM-Style Relationship Models (Salesforce/HubSpot inspired)

This shows how major CRMs handle the source/target direction problem.
They use ONE consistent direction + role labels to clarify relationships.
"""

from django.db import models
from django.core.exceptions import ValidationError
from core.models import Tenant, AuditModel, TenantValidatorMixin


class CRMRelation(AuditModel, TenantValidatorMixin):
    """
    CRM-style relationship model (Salesforce/HubSpot inspired)
    
    Convention: Always Source → Role → Target
    - Person → "Employee Of" → Organization
    - Person → "Contact For" → Organization
    - Person → "Assigned To" → WorkItem
    - WorkItem → "Depends On" → WorkItem
    
    This eliminates ambiguity by enforcing one direction.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="crm_relations")
    
    # Source (always the "from" entity)
    source_type = models.CharField(max_length=20, choices=[
        ('person', 'Person'),
        ('organization', 'Organization'), 
        ('workitem', 'Work Item'),
    ])
    source_person = models.ForeignKey('Person', null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    source_organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    source_workitem = models.ForeignKey('engagements.WorkItem', null=True, blank=True, on_delete=models.CASCADE, related_name='source_relations')
    
    # Target (always the "to" entity) 
    target_type = models.CharField(max_length=20, choices=[
        ('person', 'Person'),
        ('organization', 'Organization'),
        ('workitem', 'Work Item'),
    ])
    target_person = models.ForeignKey('Person', null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    target_organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    target_workitem = models.ForeignKey('engagements.WorkItem', null=True, blank=True, on_delete=models.CASCADE, related_name='target_relations')
    
    # Role (always describes the relationship FROM source TO target)
    role = models.ForeignKey('core.Role', on_delete=models.CASCADE)
    
    # Optional: Relationship strength/status
    is_primary = models.BooleanField(default=False, help_text="Primary relationship (e.g., primary contact)")
    is_active = models.BooleanField(default=True, help_text="Active relationship")
    
    class Meta:
        unique_together = [
            ('tenant', 'source_type', 'source_person', 'target_type', 'target_organization', 'role'),
            ('tenant', 'source_type', 'source_person', 'target_type', 'target_person', 'role'),
            ('tenant', 'source_type', 'source_organization', 'target_type', 'target_person', 'role'),
            ('tenant', 'source_type', 'source_organization', 'target_type', 'target_organization', 'role'),
            ('tenant', 'source_type', 'source_workitem', 'target_type', 'target_workitem', 'role'),
        ]
    
    def clean(self):
        """Validate that source and target are properly set based on types"""
        # Source validation
        if self.source_type == 'person' and not self.source_person:
            raise ValidationError("Source person must be set when source_type is 'person'")
        if self.source_type == 'organization' and not self.source_organization:
            raise ValidationError("Source organization must be set when source_type is 'organization'")
        if self.source_type == 'workitem' and not self.source_workitem:
            raise ValidationError("Source workitem must be set when source_type is 'workitem'")
        
        # Target validation
        if self.target_type == 'person' and not self.target_person:
            raise ValidationError("Target person must be set when target_type is 'person'")
        if self.target_type == 'organization' and not self.target_organization:
            raise ValidationError("Target organization must be set when target_type is 'organization'")
        if self.target_type == 'workitem' and not self.target_workitem:
            raise ValidationError("Target workitem must be set when target_type is 'workitem'")
    
    def get_source(self):
        """Get the source entity"""
        if self.source_type == 'person':
            return self.source_person
        elif self.source_type == 'organization':
            return self.source_organization
        elif self.source_type == 'workitem':
            return self.source_workitem
        return None
    
    def get_target(self):
        """Get the target entity"""
        if self.target_type == 'person':
            return self.target_person
        elif self.target_type == 'organization':
            return self.target_organization
        elif self.target_type == 'workitem':
            return self.target_workitem
        return None
    
    def __str__(self):
        source = self.get_source()
        target = self.get_target()
        return f"{source} → {self.role.label} → {target}"


# Example Role definitions that follow CRM conventions:
CRM_ROLE_EXAMPLES = {
    # Person → Organization relationships
    'employee_of': 'Employee Of',
    'contact_for': 'Contact For', 
    'decision_maker_for': 'Decision Maker For',
    'influencer_for': 'Influencer For',
    'technical_contact_for': 'Technical Contact For',
    
    # Person → Person relationships
    'reports_to': 'Reports To',
    'manages': 'Manages',
    'colleague_of': 'Colleague Of',
    
    # Person → WorkItem relationships
    'assigned_to': 'Assigned To',
    'reviewer_of': 'Reviewer Of',
    'stakeholder_for': 'Stakeholder For',
    
    # WorkItem → WorkItem relationships
    'depends_on': 'Depends On',
    'blocks': 'Blocks',
    'related_to': 'Related To',
    'duplicate_of': 'Duplicate Of',
    
    # Organization → Organization relationships
    'subsidiary_of': 'Subsidiary Of',
    'parent_of': 'Parent Of',
    'partner_of': 'Partner Of',
}


class SalesforceStyleRelation(AuditModel, TenantValidatorMixin):
    """
    Salesforce-style: AccountContactRelation approach
    
    Salesforce uses separate junction tables for different relationship types.
    This is their AccountContactRelation model equivalent.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="sf_relations")
    
    # Always Account → Contact (one direction)
    account = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='contact_relations')
    contact = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='account_relations')
    
    # Role describes the contact's role WITHIN the account
    role = models.CharField(max_length=50, choices=[
        ('primary_contact', 'Primary Contact'),
        ('decision_maker', 'Decision Maker'),
        ('influencer', 'Influencer'),
        ('technical_contact', 'Technical Contact'),
        ('billing_contact', 'Billing Contact'),
        ('end_user', 'End User'),
    ])
    
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [('tenant', 'account', 'contact', 'role')]
    
    def __str__(self):
        return f"{self.contact} is {self.get_role_display()} at {self.account}"


class HubSpotStyleAssociation(AuditModel, TenantValidatorMixin):
    """
    HubSpot-style: Association approach
    
    HubSpot uses association types with clear labels.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="hs_associations")
    
    # Source and target with type
    source_type = models.CharField(max_length=20, choices=[
        ('contact', 'Contact'),
        ('company', 'Company'),
        ('deal', 'Deal'),
        ('ticket', 'Ticket'),
    ])
    source_id = models.CharField(max_length=50)  # HubSpot uses string IDs
    
    target_type = models.CharField(max_length=20, choices=[
        ('contact', 'Contact'),
        ('company', 'Company'), 
        ('deal', 'Deal'),
        ('ticket', 'Ticket'),
    ])
    target_id = models.CharField(max_length=50)
    
    # Association type (HubSpot's way)
    association_type = models.CharField(max_length=50, choices=[
        ('contact_to_company', 'Contact to Company'),
        ('company_to_contact', 'Company to Contact'),
        ('deal_to_contact', 'Deal to Contact'),
        ('deal_to_company', 'Deal to Company'),
        ('ticket_to_contact', 'Ticket to Contact'),
        ('ticket_to_company', 'Ticket to Company'),
    ])
    
    # Optional: Custom labels for the association
    source_label = models.CharField(max_length=100, blank=True)  # e.g., "Primary Contact"
    target_label = models.CharField(max_length=100, blank=True)  # e.g., "Decision Maker"
    
    class Meta:
        unique_together = [('tenant', 'source_type', 'source_id', 'target_type', 'target_id', 'association_type')]
    
    def __str__(self):
        return f"{self.source_type}:{self.source_id} → {self.association_type} → {self.target_type}:{self.target_id}" 