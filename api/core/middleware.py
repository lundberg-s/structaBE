from django.utils.cache import get_cache_key, learn_cache_key
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from django.db import connection
import hashlib
import json
import time
from datetime import datetime


class QueryCountMiddleware(MiddlewareMixin):
    """
    Middleware to log query count and timing for each request.
    Provides clean, readable output instead of verbose SQL logging.
    """
    
    def process_request(self, request):
        # Reset query count for this request
        connection.queries_log.clear()
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Calculate query statistics
        query_count = len(connection.queries)
        total_query_time = sum(float(q['time']) for q in connection.queries)
        request_time = time.time() - getattr(request, '_start_time', 0)
        
        # Only log if there are queries or if it's an API request
        if query_count > 0 or request.path.startswith('/api/'):
            # Color coding based on performance
            if query_count > 10:
                emoji = "🚨"  # Too many queries
            elif query_count > 5:
                emoji = "⚠️"   # Moderate queries
            else:
                emoji = "✅"   # Good performance
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n{'─' * 60}")  # Separator line at the top
            print(f"{emoji} {request.method} {request.path} [{timestamp}]")
            print(f"   📊 Queries: {query_count} | DB Time: {total_query_time:.3f}s | Total: {request_time:.3f}s")
            
            # Show slow queries (>0.1s)
            slow_queries = [q for q in connection.queries if float(q['time']) > 0.1]
            if slow_queries:
                print(f"   🐌 Slow queries ({len(slow_queries)}):")
                for i, query in enumerate(slow_queries[:3]):  # Show top 3
                    print(f"      {i+1}. {query['time']}s - {query['sql'][:60]}...")
        
        return response


class CacheMiddleware(MiddlewareMixin):
    """
    Custom cache middleware for performance optimization.
    Caches GET requests for specific endpoints.
    """
    
    def process_request(self, request):
        # Only cache GET requests
        if request.method != 'GET':
            return None
            
        # Only cache specific endpoints
        cacheable_paths = [
            '/api/relations/persons/',
            '/api/relations/organizations/',
            '/api/relations/roles/',
            '/api/relations/relations/',
            '/api/engagements/tickets/',
            '/api/engagements/cases/',
            '/api/engagements/jobs/',
        ]
        
        if not any(request.path.startswith(path) for path in cacheable_paths):
            return None
            
        # Create cache key based on path and query parameters
        cache_key = self._get_cache_key(request)
        
        # Try to get cached response
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
            
        return None
    
    def process_response(self, request, response):
        # Only cache successful GET responses
        if (request.method != 'GET' or 
            response.status_code != 200 or
            not any(request.path.startswith(path) for path in self._get_cacheable_paths())):
            return response
            
        # Cache the response
        cache_key = self._get_cache_key(request)
        cache.set(cache_key, response, timeout=300)  # 5 minutes
        
        return response
    
    def _get_cache_key(self, request):
        """Generate a unique cache key for the request."""
        # Include tenant in cache key for multi-tenant isolation
        tenant_id = getattr(request.user, 'tenant_id', 'anonymous')
        
        # Create key from path, query params, and tenant
        key_data = {
            'path': request.path,
            'query': dict(request.GET.items()),
            'tenant': tenant_id,
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"api_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _get_cacheable_paths(self):
        """Get list of cacheable API paths."""
        return [
            '/api/relations/persons/',
            '/api/relations/organizations/',
            '/api/relations/roles/',
            '/api/relations/relations/',
            '/api/engagements/tickets/',
            '/api/engagements/cases/',
            '/api/engagements/jobs/',
        ] 