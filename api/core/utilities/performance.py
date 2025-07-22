import time
import logging
from django.db import connection
from django.conf import settings
from functools import wraps

logger = logging.getLogger(__name__)


class QueryTimer:
    """Context manager for timing database queries."""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.query_count = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.query_count = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        final_query_count = len(connection.queries)
        queries_executed = final_query_count - self.query_count
        
        logger.info(
            f"Performance: {self.operation_name} - "
            f"Duration: {duration:.3f}s, "
            f"Queries: {queries_executed}"
        )
        
        # Log slow queries
        if duration > 1.0:  # More than 1 second
            logger.warning(
                f"Slow query detected: {self.operation_name} - "
                f"Duration: {duration:.3f}s, "
                f"Queries: {queries_executed}"
            )


def performance_monitor(operation_name=None):
    """Decorator for monitoring function performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with QueryTimer(op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class DatabaseStats:
    """Utility for collecting database statistics."""
    
    @staticmethod
    def get_query_stats():
        """Get current database query statistics."""
        if not settings.DEBUG:
            return {"queries": 0, "time": 0}
        
        queries = connection.queries
        total_time = sum(float(q['time']) for q in queries)
        
        return {
            "queries": len(queries),
            "time": total_time,
            "slow_queries": len([q for q in queries if float(q['time']) > 0.1])
        }
    
    @staticmethod
    def reset_stats():
        """Reset query statistics."""
        if settings.DEBUG:
            connection.queries_log.clear()


class CacheStats:
    """Utility for monitoring cache performance."""
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics."""
        from django.core.cache import cache
        
        # This is a simplified version - in production you'd want more detailed stats
        return {
            "cache_backend": settings.CACHES['default']['BACKEND'],
            "cache_location": settings.CACHES['default']['LOCATION'],
        }


def log_performance_metrics():
    """Log comprehensive performance metrics."""
    db_stats = DatabaseStats.get_query_stats()
    cache_stats = CacheStats.get_cache_stats()
    
    logger.info(
        f"Performance Metrics - "
        f"DB Queries: {db_stats['queries']}, "
        f"DB Time: {db_stats['time']:.3f}s, "
        f"Slow Queries: {db_stats['slow_queries']}, "
        f"Cache Backend: {cache_stats['cache_backend']}"
    ) 