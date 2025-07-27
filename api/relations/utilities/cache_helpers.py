from django.core.cache import cache
from django.conf import settings
import hashlib
import json


class CacheHelper:
    """Helper class for caching operations."""
    
    @staticmethod
    def get_cache_key(prefix, **kwargs):
        """Generate a cache key with prefix and parameters."""
        key_data = {k: v for k, v in kwargs.items() if v is not None}
        key_string = json.dumps(key_data, sort_keys=True)
        return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    @staticmethod
    def cache_partner_list(tenant_id, partners, timeout=300):
        """Cache a list of partners."""
        cache_key = CacheHelper.get_cache_key('partners', tenant=tenant_id)
        cache.set(cache_key, partners, timeout=timeout)
    
    @staticmethod
    def get_cached_partner_list(tenant_id):
        """Get cached partner list."""
        cache_key = CacheHelper.get_cache_key('partners', tenant=tenant_id)
        return cache.get(cache_key)
    
    @staticmethod
    def cache_relation_list(tenant_id, relations, timeout=300):
        """Cache a list of relations."""
        cache_key = CacheHelper.get_cache_key('relations', tenant=tenant_id)
        cache.set(cache_key, relations, timeout=timeout)
    
    @staticmethod
    def get_cached_relation_list(tenant_id):
        """Get cached relation list."""
        cache_key = CacheHelper.get_cache_key('relations', tenant=tenant_id)
        return cache.get(cache_key)
    
    @staticmethod
    def cache_role_list(tenant_id, roles, timeout=300):
        """Cache a list of roles."""
        cache_key = CacheHelper.get_cache_key('roles', tenant=tenant_id)
        cache.set(cache_key, roles, timeout=timeout)
    
    @staticmethod
    def get_cached_role_list(tenant_id):
        """Get cached role list."""
        cache_key = CacheHelper.get_cache_key('roles', tenant=tenant_id)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_partner_cache(tenant_id):
        """Invalidate partner cache for a tenant."""
        cache_key = CacheHelper.get_cache_key('partners', tenant=tenant_id)
        cache.delete(cache_key)
    
    @staticmethod
    def invalidate_relation_cache(tenant_id):
        """Invalidate relation cache for a tenant."""
        cache_key = CacheHelper.get_cache_key('relations', tenant=tenant_id)
        cache.delete(cache_key)
    
    @staticmethod
    def invalidate_role_cache(tenant_id):
        """Invalidate role cache for a tenant."""
        cache_key = CacheHelper.get_cache_key('roles', tenant=tenant_id)
        cache.delete(cache_key)
    
    @staticmethod
    def invalidate_all_tenant_cache(tenant_id):
        """Invalidate all cache for a tenant."""
        CacheHelper.invalidate_partner_cache(tenant_id)
        CacheHelper.invalidate_relation_cache(tenant_id)
        CacheHelper.invalidate_role_cache(tenant_id)


def cache_decorator(timeout=300):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            cache_key = f"func_cache:{hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()}"
            
            # Try to get cached result
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator 