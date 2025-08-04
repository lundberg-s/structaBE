import uuid
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from core.models import AuditLog
from users.permissions import CanCreateEditDeleteContent, CanViewContentOnly


class BaseView:
    """Base class providing common functionality for all views."""
    
    permission_classes = [IsAuthenticated]

    def get_user(self):
        """Get the current authenticated user."""
        return self.request.user

    def get_tenant(self):
        """Get the current user's tenant."""
        return self.request.user.tenant

    def check_object_permissions(self, request, obj):
        """
        Check object-level permissions. Can be overridden by subclasses.
        By default, uses role-based permissions for content modification.
        """
        # For GET requests, use view-only permissions
        if request.method == "GET":
            if not CanViewContentOnly().has_permission(request, None):
                raise PermissionDenied("You do not have permission to view this content.")
        # For modification requests (PUT, PATCH, DELETE), check permissions
        elif request.method in ["PUT", "PATCH", "DELETE"]:
            # Users can always modify their own content
            if hasattr(obj, 'created_by') and obj.created_by == request.user.id:
                return  # Allow modification of own content
            
            # Other users need specific roles to modify content they didn't create
            if not CanCreateEditDeleteContent().has_permission(request, None):
                raise PermissionDenied("You do not have permission to modify this content.")

    def log_activity(self, instance, activity_type, action_text, **kwargs):
        """
        Professional SAP-style activity logging with forensic data.
        
        Args:
            instance: The model instance being acted upon
            activity_type: The type of activity (e.g., 'created', 'updated', 'deleted')
            action_text: Human-readable description of the action
            **kwargs: Additional data for change tracking
        """
        request = self.request
        
        # Get forensic data
        session_id = getattr(request, 'session', {}).get('session_key')
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        business_process = self.get_business_process(request)
        transaction_id = request.META.get('HTTP_X_TRANSACTION_ID') or str(uuid.uuid4())
        
        # Determine compliance category and risk level
        compliance_category = self.get_compliance_category(instance, activity_type)
        risk_level = self.assess_risk_level(instance, activity_type)
        
        # Get entity information
        entity_type = self.get_entity_type(instance)
        entity_name = self.get_entity_name(instance)
        
        # Track changes for updates
        change_summary = None
        old_values = None
        new_values = None
        
        if activity_type == 'updated' and hasattr(instance, '_state'):
            change_summary, old_values, new_values = self.get_change_data(instance)
        
        # Create the professional audit log
        AuditLog.objects.create(
            tenant=self.get_tenant(),
            entity_type=entity_type,
            entity_id=instance.id,
            entity_name=entity_name,
            created_by=self.get_user().id,
            activity_type=activity_type,
            description=f'{instance._meta.verbose_name.title()} "{entity_name}" was {action_text}.',
            change_summary=change_summary,
            old_values=old_values,
            new_values=new_values,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            business_process=business_process,
            transaction_id=transaction_id,
            compliance_category=compliance_category,
            risk_level=risk_level,
            **kwargs
        )
    
    def get_entity_type(self, instance):
        """Determine entity type from instance."""
        model_name = instance._meta.model_name.lower()
        
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
        }
        
        return entity_type_mapping.get(model_name, 'workitem')
    
    def get_entity_name(self, instance):
        """Get a human-readable name for the entity."""
        if hasattr(instance, 'title'):
            return instance.title
        elif hasattr(instance, 'name'):
            return instance.name
        elif hasattr(instance, 'first_name') and hasattr(instance, 'last_name'):
            return f"{instance.first_name} {instance.last_name}"
        elif hasattr(instance, 'key'):
            return instance.key
        else:
            return str(instance)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_business_process(self, request):
        """Determine business process from request."""
        url_patterns = {
            'tickets': 'Ticket Management',
            'cases': 'Case Management', 
            'jobs': 'Job Management',
            'persons': 'Partner Management',
            'organizations': 'Partner Management',
            'relations': 'Relationship Management',
            'comments': 'Communication Management',
            'attachments': 'Document Management',
            'assignments': 'Resource Management',
            'roles': 'Access Management',
        }
        
        for pattern, process in url_patterns.items():
            if pattern in request.path:
                return process
        return 'General'
    
    def get_compliance_category(self, instance, activity_type):
        """Determine compliance category."""
        # High-risk activities
        if activity_type in ['deleted', 'approved', 'rejected']:
            return 'security'
        elif hasattr(instance, '_meta') and instance._meta.model_name in ['person', 'organization']:
            return 'privacy'
        elif activity_type in ['exported', 'imported']:
            return 'regulatory'
        else:
            return 'operational'
    
    def assess_risk_level(self, instance, activity_type):
        """Assess risk level of the activity."""
        if activity_type in ['deleted', 'approved', 'rejected']:
            return 'high'
        elif activity_type in ['exported', 'imported']:
            return 'medium'
        else:
            return 'low'
    
    def get_change_data(self, instance):
        """Get structured change data for updates."""
        # This is a simplified version - you might want more sophisticated change tracking
        change_summary = {}
        old_values = {}
        new_values = {}
        
        if hasattr(instance, '_state') and hasattr(instance._state, 'fields_cache'):
            # Track field changes
            for field_name, old_value in instance._state.fields_cache.items():
                if hasattr(instance, field_name):
                    new_value = getattr(instance, field_name)
                    
                    # Serialize values properly for JSON storage
                    old_values[field_name] = self._serialize_value(old_value)
                    new_values[field_name] = self._serialize_value(new_value)
                    
                    change_summary[field_name] = {
                        'old': self._serialize_value(old_value),
                        'new': self._serialize_value(new_value)
                    }
        
        return change_summary, old_values, new_values

    def _serialize_value(self, value):
        """Serialize a value for JSON storage."""
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {key: self._serialize_value(val) for key, val in value.items()}
        elif hasattr(value, 'id'):
            # For model instances, store the ID and type
            return {
                'id': str(value.id),
                'type': value._meta.model_name,
                'str': str(value)
            }
        elif hasattr(value, 'isoformat'):
            # For datetime objects
            return value.isoformat()
        else:
            # Fallback to string representation
            return str(value)

    def get_tenant_queryset(self, model_class):
        """
        Get a queryset filtered by the current user's tenant.
        
        Args:
            model_class: The model class to filter
            
        Returns:
            QuerySet filtered by tenant
        """
        return model_class.objects.filter(tenant=self.get_tenant()) 