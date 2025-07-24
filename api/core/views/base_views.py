from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from engagements.models import ActivityLog
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
            if hasattr(obj, 'created_by') and obj.created_by == request.user:
                return  # Allow modification of own content
            
            # Other users need specific roles to modify content they didn't create
            if not CanCreateEditDeleteContent().has_permission(request, None):
                raise PermissionDenied("You do not have permission to modify this content.")

    def log_activity(self, instance, activity_type, action_text, work_item=None):
        """
        Log an activity for the given instance.
        
        Args:
            instance: The model instance being acted upon
            activity_type: The type of activity (e.g., 'created', 'updated', 'deleted')
            action_text: Human-readable description of the action
            work_item: Optional work item to associate with the activity log
        """
        # Determine the work item - either passed explicitly or from the instance
        if work_item is None and hasattr(instance, 'work_item'):
            work_item = instance.work_item
        elif work_item is None and hasattr(instance, '_meta') and instance._meta.model_name == 'workitem':
            work_item = instance
        
        # Create the activity log
        ActivityLog.objects.create(
            tenant=self.get_tenant(),
            work_item=work_item,
            created_by=self.get_user(),
            activity_type=activity_type,
            description=f'{instance._meta.verbose_name.title()} "{getattr(instance, "title", str(instance))}" was {action_text}.',
        )

    def get_tenant_queryset(self, model_class):
        """
        Get a queryset filtered by the current user's tenant.
        
        Args:
            model_class: The model class to filter
            
        Returns:
            QuerySet filtered by tenant
        """
        return model_class.objects.filter(tenant=self.get_tenant()) 