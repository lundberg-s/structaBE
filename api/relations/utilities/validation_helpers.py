from django.core.exceptions import ValidationError
from django.db import models


class SingleReferenceValidatorMixin:
    """Mixin to validate that exactly one of multiple fields is set."""
    
    def validate_single_reference(self, *fields):
        """Validate that exactly one of the given fields is not None."""
        if sum(getattr(self, f) is not None for f in fields) != 1:
            field_names = ', '.join(fields)
            raise ValidationError(f"Exactly one of {field_names} must be set.")


class TypeInstanceValidatorMixin:
    """Mixin to validate that a type field matches the actual instance type."""
    
    def validate_type_matches_instance(self, instance, type_field, type_mapping):
        """
        Validate that type_field matches the actual instance type.
        
        Args:
            instance: The actual object instance
            type_field: The field containing the type value
            type_mapping: Dict mapping classes to expected type values
        """
        for cls, expected_type in type_mapping.items():
            if isinstance(instance, cls) and type_field != expected_type:
                raise ValidationError(
                    f"Type must be '{expected_type}' if instance is {cls.__name__}."
                )


class TenantValidatorMixin:
    """Mixin to validate tenant consistency across related objects."""
    
    def validate_tenant_consistency(self, tenant, *objects):
        """Validate that all objects belong to the same tenant."""
        for obj in objects:
            if obj and hasattr(obj, 'tenant') and obj.tenant != tenant:
                raise ValidationError(f"{obj} does not belong to tenant {tenant}")


def validate_tenant_consistency(tenant, *objects):
    """Standalone function to validate tenant consistency."""
    for obj in objects:
        if obj and hasattr(obj, 'tenant') and obj.tenant != tenant:
            raise ValidationError(f"{obj} does not belong to tenant {tenant}")


def get_real_instance(obj):
    """Generic function to get the real instance of a polymorphic object."""
    if hasattr(obj, 'get_real_instance'):
        return obj.get_real_instance()
    return obj 