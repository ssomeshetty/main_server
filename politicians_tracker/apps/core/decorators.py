"""
DRF View Decorators for Caching and Rate Limiting
==================================================
Cache decorators and throttling decorators for high-scale API protection.
"""

from functools import wraps
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.core.cache import cache
from django.http import HttpResponseGone, JsonResponse


# =============================================================================
# CACHE DECORATORS
# =============================================================================

def cache_api_page(timeout, key_prefix=''):
    """
    Decorator to cache API view responses in Redis.
    
    Args:
        timeout: Cache timeout in seconds (e.g., 900 for 15 minutes)
        key_prefix: Optional prefix for cache key
    
    Usage:
        @cache_api_page(900)  # 15 minutes
        def my_view(request):
            ...
    
    For class-based views:
        @method_decorator(cache_api_page(900), name='dispatch')
        class MyViewSet(viewsets.ReadOnlyModelViewSet):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build cache key based on full request
            cache_key_parts = [
                'api_cache',
                key_prefix or 'default',
                request.path,
            ]
            
            # Include query parameters in cache key
            if request.GET:
                sorted_params = '&'.join(f"{k}={v}" for k, v in sorted(request.GET.items()))
                cache_key_parts.append(sorted_params)
            
            # Include language for bilingual support
            lang = request.headers.get('Accept-Language', 'en')
            cache_key_parts.append(f"lang:{lang}")
            
            cache_key = ':'.join(cache_key_parts)
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                # Add header to indicate cached response
                response = JsonResponse(cached_response['data'], status=cached_response['status'])
                response['X-Cache'] = 'HIT'
                return response
            
            # Cache miss - process request
            response = view_func(request, *args, **kwargs)
            
            # Only cache successful JSON responses
            if response.status_code == 200 and hasattr(response, 'content'):
                try:
                    cache_data = {
                        'data': response.data if hasattr(response, 'data') else {},
                        'status': response.status_code,
                    }
                    cache.set(cache_key, cache_data, timeout)
                    response['X-Cache'] = 'MISS'
                except Exception:
                    pass  # Don't fail if caching fails
            
            return response
        
        return wrapper
    return decorator


def cache_list_view(timeout=300):
    """
    Specific decorator for list views (higher timeout due to pagination).
    
    List views are cached for 5 minutes by default.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build cache key with pagination
            page = request.query_params.get('page', '1')
            cache_key = f"list:{request.path}:page:{page}"
            
            cached = cache.get(cache_key)
            if cached:
                response = JsonResponse(cached['data'], status=cached['status'])
                response['X-Cache'] = 'HIT'
                return response
            
            response = view_func(request, *args, **kwargs)
            
            if response.status_code == 200:
                cache.set(cache_key, {
                    'data': response.data if hasattr(response, 'data') else {},
                    'status': response.status_code,
                }, timeout)
                response['X-Cache'] = 'MISS'
            
            return response
        return wrapper
    return decorator


def cache_detail_view(timeout=900):
    """
    Specific decorator for detail views (longer timeout).
    
    Detail views are cached for 15 minutes by default.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Cache key includes lookup field value
            lookup_value = kwargs.get('id') or kwargs.get('pk')
            cache_key = f"detail:{request.path}:{lookup_value}"
            
            cached = cache.get(cache_key)
            if cached:
                response = JsonResponse(cached['data'], status=cached['status'])
                response['X-Cache'] = 'HIT'
                return response
            
            response = view_func(request, *args, **kwargs)
            
            if response.status_code == 200:
                cache.set(cache_key, {
                    'data': response.data if hasattr(response, 'data') else {},
                    'status': response.status_code,
                }, timeout)
                response['X-Cache'] = 'MISS'
            
            return response
        return wrapper
    return decorator


# =============================================================================
# CACHE INVALIDATION DECORATORS
# =============================================================================

def invalidate_cache_pattern(pattern):
    """
    Decorator to invalidate cache matching a pattern.
    
    Usage:
        @invalidate_cache_pattern('list:politicians:*')
        def update_politician(request, pk):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Only invalidate on successful writes
            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                if isinstance(pattern, str):
                    # Simple pattern - delete all matching keys
                    if '*' in pattern or '?' in pattern:
                        cache.delete_pattern(pattern)
                    else:
                        cache.delete(pattern)
            
            return response
        return wrapper
    return decorator


def invalidate_related_cache(model_name, instance_id):
    """
    Decorator factory to invalidate caches when a model changes.
    
    Usage:
        @invalidate_related_cache('politician', 'id')
        def update_politician(request, id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Invalidate all politician-related caches
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"detail:*politicians*{kwargs.get(instance_id)}*")
                cache.delete_pattern(f"list:*politicians*")
            
            return response
        return wrapper
    return decorator


# =============================================================================
# VARY HEADERS DECORATOR
# =============================================================================

def vary_on_language(view_func):
    """
    Decorator to vary caching on Accept-Language header.
    
    This ensures English and Kannada responses are cached separately.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Vary'] = 'Accept-Language'
        return response
    return wrapper


def vary_on_headers_decorator(*headers):
    """
    Decorator to add Vary header to response.
    
    Usage:
        @vary_on_headers_decorator('Accept-Language', 'User-Agent')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            vary = response.get('Vary', '')
            existing = vary.split(',') if vary else []
            for header in headers:
                if header not in existing:
                    existing.append(header)
            response['Vary'] = ', '.join(existing)
            return response
        return wrapper
    return decorator


# =============================================================================
# RATE LIMITING HELPERS
# =============================================================================

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def check_rate_limit(scope='default', rate='60/minute'):
    """
    Decorator to check rate limit before processing view.
    
    This provides programmatic rate limiting outside of DRF's throttle classes.
    Useful for specific endpoints that need stricter limits.
    
    Usage:
        @check_rate_limit(scope='search', rate='20/minute')
        def search_view(request):
            ...
    """
    from django.core.cache import cache
    import time
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build rate limit key
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            rate_limit_key = f"rate:{scope}:{ip}"
            
            # Parse rate (requests per period)
            requests_limit, period = rate.split('/')
            requests_limit = int(requests_limit)
            period_seconds = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[-1]]
            period_value = int(period[:-1])
            period_seconds = period_value * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[-1]]
            
            # Get current count
            current = cache.get(rate_limit_key, 0)
            
            if current >= requests_limit:
                # Rate limit exceeded
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please wait before trying again.',
                    'retry_after': period_seconds,
                }, status=429)
                response['Retry-After'] = str(period_seconds)
                response['X-RateLimit-Limit'] = str(requests_limit)
                response['X-RateLimit-Remaining'] = '0'
                response['X-RateLimit-Reset'] = str(int(time.time()) + period_seconds)
                return response
            
            # Increment counter
            cache.set(rate_limit_key, current + 1, period_seconds)
            
            # Process request
            response = view_func(request, *args, **kwargs)
            
            # Add rate limit headers
            remaining = requests_limit - current - 1
            response['X-RateLimit-Limit'] = str(requests_limit)
            response['X-RateLimit-Remaining'] = str(max(0, remaining))
            
            return response
        return wrapper
    return decorator


# =============================================================================
# BUST CACHE DECORATOR
# =============================================================================

def bust_cache(view_func):
    """
    Decorator to force fresh content (bypass cache).

    SECURITY: Requires a secret token via X-Cache-Token header.
    The token must match the CACHE_BUST_TOKEN environment variable.
    Without a valid token, cache bypass is silently ignored.

    Usage:
        @bust_cache
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        import os
        cache_bust_token = os.environ.get('CACHE_BUST_TOKEN', '')
        provided_token = request.headers.get('X-Cache-Token', '')

        # Only allow cache busting with valid secret token
        if (cache_bust_token
                and provided_token
                and cache_bust_token == provided_token):
            cache_key_parts = [
                'api_cache',
                'default',
                request.path,
            ]
            if request.GET:
                sorted_params = '&'.join(
                    f"{k}={v}" for k, v in sorted(request.GET.items())
                )
                cache_key_parts.append(sorted_params)
            cache_key = ':'.join(cache_key_parts)
            cache.delete(cache_key)

        return view_func(request, *args, **kwargs)
    return wrapper