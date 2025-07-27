from django.core.exceptions import ValidationError


class TenantValidatorMixin:
    """Mixin to validate tenant consistency across related objects."""
    
    def validate_tenant_consistency(self, tenant, *objects):
        """Validate that all objects belong to the same tenant."""
        for obj in objects:
            if obj and hasattr(obj, 'tenant') and obj.tenant != tenant:
                raise ValidationError(f"{obj} does not belong to tenant {tenant}")
        return True


def validate_tenant_consistency(tenant, *objects):
    """Standalone function to validate tenant consistency."""
    for obj in objects:
        if obj and hasattr(obj, 'tenant') and obj.tenant != tenant:
            raise ValidationError(f"{obj} does not belong to tenant {tenant}")
    return True 