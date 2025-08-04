from rest_framework import serializers
from users.models import User


class CreatedByUserField(serializers.Field):
    """Custom field to efficiently fetch User data for created_by UUIDs."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._users_cache = {}
    
    def to_representation(self, value):
        if not value:  # created_by is None
            return None
        
        # Check if we have this user in cache (for bulk operations)
        if hasattr(self, '_users_cache') and value in self._users_cache:
            user = self._users_cache[value]
        else:
            # Get the User object efficiently
            try:
                user = User.objects.get(id=value)
            except User.DoesNotExist:
                return {
                    'id': value,
                    'username': f'User {value} (not found)',
                    'email': '',
                }
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    
    @classmethod
    def prefetch_users(cls, queryset):
        """Prefetch all users for a queryset to avoid N+1 queries."""
        # Get all unique created_by UUIDs
        created_by_ids = set(queryset.values_list('created_by', flat=True).exclude(created_by__isnull=True))
        
        if not created_by_ids:
            return queryset
        
        # Fetch all users in one query
        users = User.objects.filter(id__in=created_by_ids)
        users_dict = {user.id: user for user in users}
        
        # Attach the users cache to the queryset
        queryset._users_cache = users_dict
        return queryset


class CreatedByUserMixin:
    """
    Mixin to add created_by user field to serializers.
    
    Usage:
        class MySerializer(CreatedByUserMixin, serializers.ModelSerializer):
            class Meta:
                model = MyModel
                fields = ['id', 'title', 'created_by', ...]
        
        # The mixin automatically:
        # 1. Adds a 'created_by' field that returns user data (id, username, email)
        # 2. Provides get_optimized_queryset() method for prefetching users
        
        # In your view, use:
        queryset = MySerializer.get_optimized_queryset()
    """
    
    created_by = CreatedByUserField(read_only=True)
    
    @classmethod
    def get_optimized_queryset(cls, queryset=None):
        """Return queryset optimized with user prefetching."""
        if queryset is None:
            # Get the model from the serializer
            model = cls.Meta.model
            queryset = model.objects.all()
        
        # Prefetch users to avoid N+1 queries
        queryset = CreatedByUserField.prefetch_users(queryset)
        
        return queryset 