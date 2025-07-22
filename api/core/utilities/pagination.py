from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class OptimizedPageNumberPagination(PageNumberPagination):
    """Optimized pagination with performance improvements."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def paginate_queryset(self, queryset, request, view=None):
        """Override to add performance optimizations."""
        
        # Add select_related and prefetch_related if not already present
        if hasattr(queryset, '_prefetch_related_lookups'):
            # Already optimized
            pass
        else:
            # Add basic optimizations
            if hasattr(queryset.model, 'select_related_fields'):
                queryset = queryset.select_related(*queryset.model.select_related_fields)
            if hasattr(queryset.model, 'prefetch_related_fields'):
                queryset = queryset.prefetch_related(*queryset.model.prefetch_related_fields)
        
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        """Enhanced response with performance metrics."""
        response = super().get_paginated_response(data)
        
        # Add performance hints
        response.data['performance'] = {
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
        }
        
        return response


class CursorPagination(PageNumberPagination):
    """Cursor-based pagination for better performance with large datasets."""
    
    page_size = 100
    cursor_query_param = 'cursor'
    ordering = '-created_at'
    
    def paginate_queryset(self, queryset, request, view=None):
        """Cursor-based pagination implementation."""
        cursor = request.query_params.get(self.cursor_query_param)
        page_size = self.get_page_size(request)
        
        if cursor:
            # Decode cursor and filter queryset
            try:
                cursor_value = self.decode_cursor(cursor)
                queryset = queryset.filter(created_at__lt=cursor_value)
            except:
                pass
        
        # Limit to page size + 1 to check if there's a next page
        queryset = queryset[:page_size + 1]
        
        has_next = len(queryset) > page_size
        if has_next:
            queryset = queryset[:-1]
        
        self.page = queryset
        self.has_next = has_next
        
        return queryset
    
    def get_paginated_response(self, data):
        """Return response with cursor pagination info."""
        response_data = {
            'results': data,
            'has_next': self.has_next,
        }
        
        if self.has_next and self.page:
            # Create next cursor
            last_item = self.page[-1] if self.page else None
            if last_item:
                next_cursor = self.encode_cursor(last_item.created_at)
                response_data['next_cursor'] = next_cursor
        
        return Response(response_data)
    
    def encode_cursor(self, value):
        """Encode cursor value."""
        import base64
        return base64.b64encode(str(value).encode()).decode()
    
    def decode_cursor(self, cursor):
        """Decode cursor value."""
        import base64
        from datetime import datetime
        decoded = base64.b64decode(cursor.encode()).decode()
        return datetime.fromisoformat(decoded)


class PerformancePaginator(Paginator):
    """Performance-optimized paginator."""
    
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        
        # Add performance optimizations
        if hasattr(object_list, 'model'):
            self._optimize_queryset(object_list)
    
    def _optimize_queryset(self, queryset):
        """Apply query optimizations."""
        if not isinstance(queryset, QuerySet):
            return
        
        # Add common optimizations
        if hasattr(queryset.model, 'select_related_fields'):
            queryset = queryset.select_related(*queryset.model.select_related_fields)
        if hasattr(queryset.model, 'prefetch_related_fields'):
            queryset = queryset.prefetch_related(*queryset.model.prefetch_related_fields)
    
    def get_page(self, number):
        """Get page with performance optimizations."""
        try:
            page = super().get_page(number)
            # Add performance metadata
            page.performance_metrics = {
                'total_count': self.count,
                'total_pages': self.num_pages,
                'current_page': number,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
            }
            return page
        except (EmptyPage, PageNotAnInteger):
            return self.get_page(1) 