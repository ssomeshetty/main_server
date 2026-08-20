from rest_framework.pagination import CursorPagination


class CustomCursorPagination(CursorPagination):
    """
    Custom cursor-based pagination for high-performance list views.

    Features:
    - Cursor-based pagination (no OFFSET performance degradation)
    - Configurable page size via ?page_size=N
    - Consistent ordering via indexed fields
    - Optimized for large datasets

    Usage:
    - Set as DEFAULT_PAGINATION_CLASS in REST_FRAMEWORK settings
    - Override in ViewSet: pagination_class = CustomCursorPagination
    """

    # Page size defaults
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    # Ordering (must use indexed field for performance)
    ordering = '-id'

    # Cursor description
    cursor_query_param = 'cursor'

    def get_page_size(self, request):
        """Get page size with security limits."""
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size:
            try:
                page_size = int(page_size)
                if page_size > self.max_page_size:
                    return self.max_page_size
                if page_size <= 0:
                    return self.page_size
                return page_size
            except (ValueError, TypeError):
                return self.page_size
        return self.page_size


class OptimizedCursorPagination(CursorPagination):
    """
    Optimized cursor pagination specifically for the politician tracker.

    Tuned for high-volume list views with bilingual content delivery
    and multiple filter combinations.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

    # Use indexed field for default ordering
    ordering = '-id'

    def get_page_size(self, request):
        """Get page size with security limits."""
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size:
            try:
                page_size = int(page_size)
                if page_size > self.max_page_size:
                    return self.max_page_size
                if page_size <= 0:
                    return self.page_size
                return page_size
            except (ValueError, TypeError):
                return self.page_size
        return self.page_size


class LargeResultsSetPagination(CursorPagination):
    """
    Cursor pagination for large result sets (thousands of results).
    """

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-id'


class SmallResultsSetPagination(CursorPagination):
    """
    Cursor pagination for small result sets.
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 25
    ordering = '-id'