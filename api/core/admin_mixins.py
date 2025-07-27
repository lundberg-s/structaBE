from django.contrib import admin
from core.models import AuditLog
import uuid


class AdminAuditMixin:
    """
    Reusable mixin for Django admin classes to automatically add audit logging.
    
    Usage:
        @admin.register(YourModel)
        class YourModelAdmin(AdminAuditMixin, admin.ModelAdmin):
            # Your admin configuration here
            pass
    """
    
    def save_model(self, request, obj, form, change):
        """Override to add audit logging for admin operations."""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # Create audit log
        activity_type = 'created' if is_new else 'updated'
        description = self.get_audit_description(obj, activity_type)
        
        AuditLog.objects.create(
            tenant=getattr(obj, 'tenant', None),
            entity_type=self.get_entity_type(obj),
            entity_id=obj.id,
            entity_name=self.get_entity_name(obj),
            created_by=request.user,
            activity_type=activity_type,
            description=description,
            risk_level=self.get_risk_level(obj, activity_type),
            compliance_category=self.get_compliance_category(obj, activity_type),
            business_process=self.get_business_process(obj),
            transaction_id=str(uuid.uuid4()),
            session_id=getattr(request.session, 'session_key', None),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    
    def delete_model(self, request, obj):
        """Override to add audit logging for deletion."""
        # Create audit log before deletion
        AuditLog.objects.create(
            tenant=getattr(obj, 'tenant', None),
            entity_type=self.get_entity_type(obj),
            entity_id=obj.id,
            entity_name=self.get_entity_name(obj),
            created_by=request.user,
            activity_type='deleted',
            description=self.get_audit_description(obj, 'deleted'),
            risk_level=self.get_risk_level(obj, 'deleted'),
            compliance_category=self.get_compliance_category(obj, 'deleted'),
            business_process=self.get_business_process(obj),
            transaction_id=str(uuid.uuid4()),
            session_id=getattr(request.session, 'session_key', None),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        super().delete_model(request, obj)
    
    def get_entity_type(self, obj):
        """Get the entity type for audit logging. Override in subclasses if needed."""
        model_name = obj._meta.model_name.lower()
        
        # Common entity type mappings
        entity_type_mapping = {
            'workitem': 'workitem',
            'ticket': 'ticket',
            'case': 'case',
            'job': 'job',
            'person': 'person',
            'organization': 'organization',
            'relation': 'relation',
            'comment': 'comment',
            'attachment': 'attachment',
            'assignment': 'assignment',
            'role': 'role',
            'partner': 'partner',  # Base class for person/organization
            'user': 'user',
            'tenant': 'tenant',
        }
        
        return entity_type_mapping.get(model_name, model_name)
    
    def get_entity_name(self, obj):
        """Get a human-readable name for the entity. Override in subclasses if needed."""
        if hasattr(obj, 'title'):
            return obj.title
        elif hasattr(obj, 'name'):
            return obj.name
        elif hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
            return f"{obj.first_name} {obj.last_name}"
        elif hasattr(obj, 'key'):
            return obj.key
        else:
            return str(obj)
    
    def get_audit_description(self, obj, activity_type):
        """Get audit description. Override in subclasses if needed."""
        entity_name = self.get_entity_name(obj)
        model_verbose_name = obj._meta.verbose_name.title()
        return f'{model_verbose_name} "{entity_name}" was {activity_type} via admin interface.'
    
    def get_risk_level(self, obj, activity_type):
        """Get risk level for the activity. Override in subclasses if needed."""
        if activity_type in ['deleted', 'approved', 'rejected']:
            return 'high'
        elif activity_type in ['exported', 'imported']:
            return 'medium'
        else:
            return 'low'
    
    def get_compliance_category(self, obj, activity_type):
        """Get compliance category. Override in subclasses if needed."""
        if activity_type in ['deleted', 'approved', 'rejected']:
            return 'security'
        elif hasattr(obj, '_meta') and obj._meta.model_name in ['person', 'organization']:
            return 'privacy'
        elif activity_type in ['exported', 'imported']:
            return 'regulatory'
        else:
            return 'operational'
    
    def get_business_process(self, obj):
        """Get business process. Override in subclasses if needed."""
        model_name = obj._meta.model_name.lower()
        
        process_mapping = {
            'ticket': 'Ticket Management',
            'case': 'Case Management', 
            'job': 'Job Management',
            'person': 'Partner Management',
            'organization': 'Partner Management',
            'relation': 'Relationship Management',
            'comment': 'Communication Management',
            'attachment': 'Document Management',
            'assignment': 'Resource Management',
            'role': 'Access Management',
            'partner': 'Partner Management',
            'user': 'Access Management',
        }
        
        return process_mapping.get(model_name, 'General')
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 